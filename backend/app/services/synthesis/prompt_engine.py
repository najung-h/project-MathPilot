"""Prompt Engine - LLM 프롬프트 구성"""

from dataclasses import dataclass

from app.services.synthesis.segment_mapper import MappedSegment


@dataclass
class PromptContext:
    """LLM 프롬프트 컨텍스트"""

    slide_number: int
    system_prompt: str
    user_prompt: str
    requires_sos_explanation: bool = False


class PromptEngine:
    """
    OCR + STT + SOS 정보를 LLM 프롬프트로 구성

    슬라이드별로 적절한 프롬프트 생성
    """

    SYSTEM_PROMPT_SUMMARY = """너는 대학원생 조교야.
슬라이드 내용(OCR)과 강사의 말(STT)을 합쳐서 완벽한 요약 노트를 만들어.

규칙:
1. 슬라이드의 구조(제목, 본문, 수식)를 유지해
2. 강사의 설명 중 중요한 내용을 본문에 통합해
3. 수식은 LaTeX 형식 유지 ($...$ 또는 $$...$$)
4. 강사만 말하고 슬라이드에 없는 내용은 > 인용구로 추가해
5. 간결하고 핵심적인 내용만 포함해

출력 형식: 마크다운
"""

    SYSTEM_PROMPT_SOS = """너는 친절한 과외 선생님이야.
학생이 이해하기 어려워한 부분에 대해 상세한 설명을 제공해줘.

규칙:
1. 어려운 개념을 쉬운 예시로 설명해
2. 수식이 있다면 각 부분의 의미를 풀어서 설명해
3. 단계별로 논리적 흐름을 보여줘
4. 필요하다면 그 개념이 왜 중요한지도 언급해
5. 학생이 스스로 이해할 수 있도록 유도해

출력 형식:
💡 **심층 해설**

[상세 설명 내용]
"""

    def build_summary_prompt(self, segment: MappedSegment) -> PromptContext:
        """
        요약 노트 생성을 위한 프롬프트 구성

        Args:
            segment: 매핑된 세그먼트

        Returns:
            프롬프트 컨텍스트
        """
        user_prompt = f"""## 슬라이드 {segment.slide_number} 내용 (OCR)

{segment.ocr_content}

## 강사 설명 (STT)

{segment.audio_transcript}

---

위 내용을 바탕으로 요약 노트를 작성해줘.
"""

        return PromptContext(
            slide_number=segment.slide_number,
            system_prompt=self.SYSTEM_PROMPT_SUMMARY,
            user_prompt=user_prompt,
            requires_sos_explanation=segment.sos_requested,
        )

    def build_sos_prompt(self, segment: MappedSegment) -> PromptContext:
        """
        SOS 심층 해설을 위한 프롬프트 구성

        Args:
            segment: SOS가 요청된 세그먼트

        Returns:
            프롬프트 컨텍스트
        """
        # SOS 구간의 구체적인 텍스트 사용
        transcript_text = segment.sos_transcript or segment.audio_transcript
        
        user_prompt = f"""학생이 아래 내용을 이해하기 어려워합니다.

## 슬라이드 내용

{segment.ocr_content}

## 교수님이 말씨하신 부분

"{transcript_text}"

라고 교수님이 말씨하신 부분 잘 모르겠어요. 이 부분에 대해 상세하게 설명해주세요.
"""

        return PromptContext(
            slide_number=segment.slide_number,
            system_prompt=self.SYSTEM_PROMPT_SOS,
            user_prompt=user_prompt,
            requires_sos_explanation=True,
        )

    def build_prompts(
        self,
        segments: list[MappedSegment],
    ) -> list[PromptContext]:
        """
        모든 세그먼트에 대한 프롬프트 목록 생성

        Args:
            segments: 매핑된 세그먼트 목록

        Returns:
            프롬프트 컨텍스트 목록
        """
        prompts = []
        for segment in segments:
            # 기본 요약 프롬프트
            prompts.append(self.build_summary_prompt(segment))

            # SOS 요청이 있으면 추가 프롬프트
            if segment.sos_requested:
                prompts.append(self.build_sos_prompt(segment))

        return prompts
