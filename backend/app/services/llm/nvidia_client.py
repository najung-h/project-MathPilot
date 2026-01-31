"""NVIDIA NIM LLM Client"""

from typing import Any
import base64
from app.services.llm.base import BaseLLMClient


class NvidiaClient(BaseLLMClient):
    """
    NVIDIA NIM API 클라이언트 (OpenAI SDK 호환)
    
    Vision: meta/llama-3.2-90b-vision-instruct
    Text: meta/llama-3.3-70b-instruct
    """

    def __init__(
        self,
        api_key: str,
        model: str = "meta/llama-3.3-70b-instruct",
        vision_model: str = "meta/llama-3.2-90b-vision-instruct",
        temperature: float = 0.3,
        max_tokens: int = 1024,
        base_url: str = "https://integrate.api.nvidia.com/v1",
    ):
        self.api_key = api_key
        self.model = model
        self.vision_model = vision_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
        return self._client

    async def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        client = self._get_client()
        
        response = await client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content or ""

    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        client = self._get_client()
        print(f"[DEBUG] NvidiaClient Base URL: {client.base_url}")
        
        # Base64 인코딩
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        print(f"[DEBUG] NVIDIA Vision Request: Model={self.vision_model}, Image Size={len(image_bytes)} bytes")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })
        
        try:
            response = await client.chat.completions.create(
                model=kwargs.get("model", self.vision_model),
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"[ERROR] NVIDIA Vision Failed: {e}")
            raise

    async def analyze_image_url(
        self,
        image_url: str,
        prompt: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        # 로컬 환경에서는 URL 분석 대신 analyze_image를 사용하도록 안내하거나
        # 이미지 다운로드 후 처리가 필요함. 여기서는 NotImplementedError로 남겨둠.
        # 실제 서비스 로직에서는 download -> analyze_image 흐름을 타므로 문제 없음.
        raise NotImplementedError("Use analyze_image with bytes for local files")
