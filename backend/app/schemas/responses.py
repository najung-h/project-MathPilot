"""Response Schemas - 모든 API 응답 스키마"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


# ==================== Video Responses ====================


class UploadResponse(BaseModel):
    """파일 업로드 응답"""

    task_id: str = Field(..., description="작업 ID (UUID)")
    file_url: str = Field(..., description="파일 URL (정적 경로)")
    status: Literal["uploaded"] = Field(..., description="상태")


class ProcessVideoResponse(BaseModel):
    """비디오 처리 시작 응답"""

    task_id: str = Field(..., description="작업 ID")
    status: Literal["processing"] = Field(..., description="상태")
    estimated_time_sec: int = Field(..., description="예상 처리 시간 (초)")


class ProgressDetail(BaseModel):
    """진행률 상세"""

    vision: float = Field(..., ge=0.0, le=1.0, description="Vision 처리 진행률")
    audio: float = Field(..., ge=0.0, le=1.0, description="Audio 처리 진행률")
    synthesis: float = Field(..., ge=0.0, le=1.0, description="Synthesis 진행률")


class TaskStatusResponse(BaseModel):
    """작업 상태 조회 응답"""

    task_id: str = Field(..., description="작업 ID")
    status: Literal["pending", "uploaded", "processing", "completed", "failed"] = Field(
        ..., description="작업 상태"
    )
    progress: ProgressDetail = Field(..., description="진행률 상세")
    error_message: str | None = Field(None, description="에러 메시지 (실패 시)")


# ==================== Note Responses ====================


class SlideDetail(BaseModel):
    """슬라이드 상세 정보"""

    slide_number: int = Field(..., description="슬라이드 번호")
    timestamp_start: float = Field(..., description="시작 타임스탬프 (초)")
    timestamp_end: float = Field(..., description="종료 타임스탬프 (초)")
    image_url: str = Field(..., description="슬라이드 이미지 URL (Presigned)")
    ocr_content: str = Field(..., description="OCR 결과 (LaTeX 포함 마크다운)")
    audio_summary: str = Field(..., description="해당 구간 음성 요약")
    sos_explanation: str | None = Field(None, description="SOS 심층 해설")


class NoteResponse(BaseModel):
    """노트 조회 응답"""

    task_id: str = Field(..., description="작업 ID")
    title: str = Field(..., description="노트 제목")
    slides: list[SlideDetail] = Field(..., description="슬라이드 목록")
    created_at: datetime = Field(..., description="생성 시간")


class NoteDownloadResponse(BaseModel):
    """노트 다운로드 URL 응답"""

    download_url: str = Field(..., description="다운로드 URL (Presigned)")
    filename: str = Field(..., description="파일명")
    expires_at: datetime = Field(..., description="URL 만료 시간")


class SlideImageResponse(BaseModel):
    """슬라이드 이미지 URL 응답"""

    image_url: str = Field(..., description="이미지 URL (Presigned)")
    expires_at: datetime = Field(..., description="URL 만료 시간")


# ==================== Common Responses ====================


class ErrorResponse(BaseModel):
    """에러 응답"""

    detail: str = Field(..., description="에러 상세 메시지")


class HealthResponse(BaseModel):
    """헬스체크 응답"""

    status: Literal["healthy", "unhealthy"] = Field(..., description="상태")
