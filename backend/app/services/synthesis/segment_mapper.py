"""Segment Mapper - Vision-Audio 타임스탬프 매핑"""

from dataclasses import dataclass

from app.services.vision.scene_detector import DetectedSlide
from app.services.vision.ocr_processor import OCRResult
from app.services.audio.stt_processor import TranscriptSegment


@dataclass
class MappedSegment:
    """Vision-Audio 매핑된 세그먼트"""

    slide_number: int
    timestamp_start: float
    timestamp_end: float
    ocr_content: str  # 슬라이드 OCR 결과
    audio_transcript: str  # 해당 구간 음성 전사
    sos_requested: bool = False  # SOS 요청 여부
    sos_transcript: str = ""  # SOS 구간의 구체적인 텍스트

class SegmentMapper:
    """
    슬라이드 타임스탬프를 기준으로 오디오 전사 분할

    각 슬라이드에 해당하는 음성 내용을 매핑
    """

    def __init__(self, padding_sec: float = 5.0):
        """
        Args:
            padding_sec: 슬라이드 전환 시 앞뒤 패딩 (싱크 오류 방지)
        """
        self.padding_sec = padding_sec

    def map_segments(
        self,
        slides: list[DetectedSlide],
        ocr_results: list[OCRResult],
        transcript_segments: list[TranscriptSegment],
        sos_timestamps: list[float] | None = None,
    ) -> list[MappedSegment]:
        """
        슬라이드와 오디오 전사를 매핑

        Args:
            slides: 감지된 슬라이드 목록
            ocr_results: OCR 결과 목록
            transcript_segments: 음성 전사 세그먼트 목록
            sos_timestamps: SOS 요청 타임스탬프 목록

        Returns:
            매핑된 세그먼트 목록
        """
        sos_timestamps = sos_timestamps or []
        mapped_segments = []

        for slide, ocr_result in zip(slides, ocr_results):
            # 슬라이드 구간 (패딩 적용)
            start = max(0, slide.timestamp_start - self.padding_sec)
            end = slide.timestamp_end + self.padding_sec

            # 해당 구간의 전사 추출
            relevant_transcripts = [
                seg.text
                for seg in transcript_segments
                if self._overlaps(seg.start, seg.end, start, end)
            ]
            audio_transcript = " ".join(relevant_transcripts)

            # SOS 요청 확인 및 SOS 구간 텍스트 추출
            sos_requested = False
            sos_transcript = ""
            
            for sos_ts in sos_timestamps:
                if start <= sos_ts <= end:
                    sos_requested = True
                    # SOS 타임스탬프 주변 텍스트 추출 (더 넓은 패딩)
                    sos_padding = 10.0  # SOS 구간 전후 10초
                    sos_start = max(0, sos_ts - sos_padding)
                    sos_end = sos_ts + sos_padding
                    
                    sos_texts = [
                        seg.text
                        for seg in transcript_segments
                        if self._overlaps(seg.start, seg.end, sos_start, sos_end)
                    ]
                    sos_transcript = " ".join(sos_texts)
                    break  # 첨 번째 SOS만 처리

            mapped_segments.append(
                MappedSegment(
                    slide_number=slide.slide_number,
                    timestamp_start=slide.timestamp_start,
                    timestamp_end=slide.timestamp_end,
                    ocr_content=ocr_result.structured_markdown,
                    audio_transcript=audio_transcript,
                    sos_requested=sos_requested,
                    sos_transcript=sos_transcript,
                )
            )

        return mapped_segments

    def _overlaps(
        self,
        start1: float,
        end1: float,
        start2: float,
        end2: float,
    ) -> bool:
        """두 시간 구간이 겹치는지 확인"""
        return start1 < end2 and end1 > start2
