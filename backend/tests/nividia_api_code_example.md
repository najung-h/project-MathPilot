```
import os
import riva.client

# 1. 인증 및 모델 연결 (Initialization)
auth = riva.client.Auth(
    None,
    use_ssl=True,
    uri="grpc.nvcf.nvidia.com:443",
    metadata_args=[
        ("function-id", "b702f636-f60c-4a3d-a6f4-f3568c13bd7d"), # Whisper Large v3 ID
        ("authorization", f"Bearer {os.environ.get('NVIDIA_API_KEY')}")
    ]
)

# 2. ASR 서비스 인스턴스 생성
asr_service = riva.client.ASRService(auth)

# 3. 모델 설정 (한국어, 16kHz 필수)
config = riva.client.RecognitionConfig(
    encoding=riva.client.AudioEncoding.LINEAR_PCM,
    sample_rate_hertz=16000,       # 주의: 입력 오디오는 무조건 16000Hz여야 함
    language_code="ko-KR",         # 한국어 지정
    max_alternatives=1,
    enable_automatic_punctuation=True,
    verbatim_transcripts=False
)

# 4. 추론 실행 함수
def transcribe(audio_bytes: bytes) -> str:
    # Riva 서버로 전송 및 추론
    response = asr_service.offline_recognize(audio_bytes, config)
    
    # 결과 추출 (가장 확률 높은 텍스트)
    if len(response.results) > 0 and len(response.results[0].alternatives) > 0:
        return response.results[0].alternatives[0].transcript
    return ""
```



    import requests, base64
    import os
    
    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    stream = True
    
    headers = {
      "Authorization": f"Bearer {os.environ.get('NVIDIA_API_KEY')}", # <-- 수정됨 (f-string 사용)
      "Accept": "text/event-stream" if stream else "application/json"
    }
    
    payload = {
      "model": "meta/llama-3.2-90b-vision-instruct",
      "messages": [{"role":"user","content":""}],
      "max_tokens": 512,
      "temperature": 1.00,
      "top_p": 1.00,
      "frequency_penalty": 0.00,
      "presence_penalty": 0.00,
      "stream": stream
    }
    
    response = requests.post(invoke_url, headers=headers, json=payload)
    
    if stream:
        for line in response.iter_lines():
            if line:
                print(line.decode("utf-8"))
    else:
        print(response.json())


```
from openai import OpenAI
import os

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.environ.get("NVIDIA_API_KEY") # <-- 수정됨
)

completion = client.chat.completions.create(
  model="meta/llama-3.3-70b-instruct",
  messages=[{"role":"user","content":""}],
  temperature=0.2,
  top_p=0.7,
  max_tokens=1024,
  stream=True
)

for chunk in completion:
  if chunk.choices and chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")
```
