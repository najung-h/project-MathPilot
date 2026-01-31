"""Note Generator - 마크다운 노트 생성"""

from dataclasses import dataclass
from datetime import datetime

from app.services.llm.base import BaseLLMClient
from app.services.synthesis.segment_mapper import MappedSegment
from app.services.synthesis.prompt_engine import PromptEngine, PromptContext


@dataclass
class GeneratedSlide:
    """생성된 슬라이드 노트"""

    slide_number: int
    timestamp_start: float
    timestamp_end: float
    image_s3_key: str
    summary_content: str  # LLM이 생성한 요약
    sos_explanation: str | None = None  # SOS 심층 해설


@dataclass
class GeneratedNote:
    """생성된 전체 노트"""

    title: str
    slides: list[GeneratedSlide]
    created_at: datetime
    markdown_content: str  # 전체 마크다운 문서


class NoteGenerator:
    """
    LLM 응답을 마크다운 문서로 조합

    최종 단권화 노트 생성
    """

    def __init__(self, llm_client: BaseLLMClient):
        """
        Args:
            llm_client: LLM 클라이언트
        """
        self.llm_client = llm_client
        self.prompt_engine = PromptEngine()

    async def generate_note(
        self,
        segments: list[MappedSegment],
        slide_image_keys: list[str],
        title: str = "강의 노트",
    ) -> GeneratedNote:
        """
        전체 노트 생성

        Args:
            segments: 매핑된 세그먼트 목록
            slide_image_keys: 슬라이드 이미지 S3 키 목록
            title: 노트 제목

        Returns:
            생성된 노트
        """
        generated_slides = []

        for segment, image_key in zip(segments, slide_image_keys):
            # 디버깅: 세그먼트 정보 출력
            print(f"[Slide {segment.slide_number}] OCR length: {len(segment.ocr_content)}, Audio transcript length: {len(segment.audio_transcript)}")
            print(f"[Slide {segment.slide_number}] Audio transcript preview: {segment.audio_transcript[:200] if segment.audio_transcript else 'EMPTY'}...")
            
            # 요약 생성
            summary_prompt = self.prompt_engine.build_summary_prompt(segment)
            summary_content = await self._generate_content(summary_prompt)

            # SOS 해설 생성 (요청된 경우)
            sos_explanation = None
            if segment.sos_requested:
                sos_prompt = self.prompt_engine.build_sos_prompt(segment)
                sos_explanation = await self._generate_content(sos_prompt)

            generated_slides.append(
                GeneratedSlide(
                    slide_number=segment.slide_number,
                    timestamp_start=segment.timestamp_start,
                    timestamp_end=segment.timestamp_end,
                    image_s3_key=image_key,
                    summary_content=summary_content,
                    sos_explanation=sos_explanation,
                )
            )

        # 마크다운 문서 조합
        markdown_content = self._build_markdown(title, generated_slides)

        return GeneratedNote(
            title=title,
            slides=generated_slides,
            created_at=datetime.now(),
            markdown_content=markdown_content,
        )

    async def _generate_content(self, prompt: PromptContext) -> str:
        """LLM으로 콘텐츠 생성"""
        from app.utils.text_cleaner import clean_hallucinations

        response = await self.llm_client.chat(
            messages=[
                {"role": "system", "content": prompt.system_prompt},
                {"role": "user", "content": prompt.user_prompt},
            ]
        )
        # 환각(반복 패턴) 제거
        return clean_hallucinations(response)

    def _build_markdown(
        self,
        title: str,
        slides: list[GeneratedSlide],
    ) -> str:
        """전체 마크다운 문서 조합"""
        lines = [
            f"# {title}",
            "",
            f"_생성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
            "",
            "---",
            "",
        ]

        for slide in slides:
            # 타임스탬프
            start_min = int(slide.timestamp_start // 60)
            start_sec = int(slide.timestamp_start % 60)
            lines.append(f"## 슬라이드 {slide.slide_number} ({start_min:02d}:{start_sec:02d})")
            lines.append("")

            # 요약 내용
            lines.append(slide.summary_content)
            lines.append("")

            # SOS 해설 (있는 경우)
            if slide.sos_explanation:
                lines.append("")
                lines.append(slide.sos_explanation)
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)
