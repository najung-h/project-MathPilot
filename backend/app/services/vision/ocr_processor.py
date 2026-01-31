"""OCR Processor - Vision LLM 기반 OCR + LaTeX 변환"""

from dataclasses import dataclass
import re

from app.services.llm.base import BaseLLMClient
from app.services.vision.scene_detector import DetectedSlide


@dataclass
class OCRResult:
    """OCR 결과"""

    slide_number: int
    raw_text: str
    structured_markdown: str  # 구조화된 마크다운 (제목, 본문, 수식 구분)
    latex_expressions: list[str]  # 추출된 LaTeX 수식 목록


class OCRProcessor:
    """
    Vision LLM을 사용하여 슬라이드 이미지에서 텍스트 및 수식 추출

    GPT-4o-vision 또는 Gemini Vision 사용
    """

    SYSTEM_PROMPT = """너는 수학 강의 슬라이드를 분석하는 전문가야.
이미지에서 텍스트와 수식을 정확하게 추출해서 마크다운 형식으로 변환해줘.

규칙:
1. 제목은 # 또는 ##으로 표시
2. 수식은 반드시 LaTeX 형식으로 변환 (인라인: $...$, 블록: $$...$$)
3. 리스트는 - 또는 숫자로 표시
4. 표가 있으면 마크다운 테이블로 변환
5. 중요한 내용은 **굵게** 표시
6. [중요] LaTeX 수식 작성 시 \\begin{array} 등의 환경을 과도하게 중첩하지 마시오. 단순하고 명확하게 작성할 것.

출력 형식:
```markdown
# 슬라이드 제목

본문 내용...

수식이 있으면:
$$
\\int_0^\\infty f(x) dx
$$
```
"""

    def __init__(self, llm_client: BaseLLMClient):
        """
        Args:
            llm_client: Vision 기능을 지원하는 LLM 클라이언트
        """
        self.llm_client = llm_client

    async def process_slide(
        self,
        slide: DetectedSlide,
        image_bytes: bytes,
    ) -> OCRResult:
        """
        단일 슬라이드 OCR 처리

        Args:
            slide: 감지된 슬라이드 정보
            image_bytes: 슬라이드 이미지 바이트

        Returns:
            OCR 결과 (구조화된 마크다운 포함)
        """
        # Vision LLM 호출
        response = await self.llm_client.analyze_image(
            image_bytes=image_bytes,
            prompt="이 슬라이드의 내용을 마크다운으로 변환해줘. 수식은 LaTeX로.",
            system_prompt=self.SYSTEM_PROMPT,
        )

        # 환각(반복) 패턴 정제
        cleaned_response = self._clean_hallucinations(response)

        # LaTeX 수식 추출
        latex_expressions = self._extract_latex(cleaned_response)

        return OCRResult(
            slide_number=slide.slide_number,
            raw_text=response,
            structured_markdown=cleaned_response,
            latex_expressions=latex_expressions,
        )

    async def process_slides(
        self,
        slides: list[DetectedSlide],
        image_bytes_list: list[bytes],
    ) -> list[OCRResult]:
        """
        여러 슬라이드 일괄 OCR 처리

        Args:
            slides: 감지된 슬라이드 목록
            image_bytes_list: 각 슬라이드의 이미지 바이트 목록

        Returns:
            OCR 결과 목록
        """
        results = []
        for slide, image_bytes in zip(slides, image_bytes_list):
            result = await self.process_slide(slide, image_bytes)
            results.append(result)
        return results

    def _clean_hallucinations(self, text: str) -> str:
        """
        LLM 환각으로 인한 반복 텍스트/수식 제거
        예: \begin{array}{c}가 5회 이상 반복되는 경우 등
        """
        # 1. 과도한 중첩 구조 제거 (\begin{array}{c}가 3회 이상 연속 중첩되면 삭제)
        # 정규식: (\begin{array}{c}\s*){3,} -> 제거 또는 단순화
        # 하지만 정규식으로는 중첩 괄호 처리가 어려우므로, 단순 반복 패턴만 잡음
        
        # 특정 키워드가 너무 많이 반복되면 해당 줄을 잘라냄
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # \begin{array}가 한 줄에 3번 이상 나오거나, 전체적으로 너무 긴 줄은 의심
            if line.count(r'\begin{array}') > 3:
                continue
            
            # \begin{array}{c} 패턴의 무한 반복 감지
            if len(line) > 500 and r'\begin{array}' in line:
                 # 너무 긴 수식 줄은 환각일 가능성이 높으므로 스킵 (안전장치)
                 continue
                 
            cleaned_lines.append(line)
            
        return '\n'.join(cleaned_lines)

    def _extract_latex(self, markdown_text: str) -> list[str]:
        """
        마크다운 텍스트에서 LaTeX 수식 추출

        Args:
            markdown_text: 마크다운 텍스트

        Returns:
            LaTeX 수식 목록
        """
        # 블록 수식 추출 ($$...$$)
        block_pattern = r"\$\$(.*?)\$\$"
        block_matches = re.findall(block_pattern, markdown_text, re.DOTALL)

        # 인라인 수식 추출 ($...$)
        inline_pattern = r"(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)"
        inline_matches = re.findall(inline_pattern, markdown_text)

        return block_matches + inline_matches
