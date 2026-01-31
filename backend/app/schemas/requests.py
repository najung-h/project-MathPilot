"""Request Schemas - 모든 API 요청 스키마"""

from pydantic import BaseModel, Field


# ==================== Video Requests ====================


class VideoUrlRequest(BaseModel):
    """URL 비디오 다운로드 요청"""

    url: str = Field(..., description="비디오 URL (YouTube 등)", examples=["https://youtu.be/example"])
    sos_timestamps: list[float] = Field(
        default_factory=list,
        description="SOS 요청 타임스탬프 목록 (초)",
    )



class ProcessingOptions(BaseModel):
    """비디오 처리 옵션"""

    frame_interval_sec: float | None = Field(
        default=None,
        ge=0.1,
        le=10.0,
        description="프레임 추출 간격 (초)",
    )
    ssim_threshold: float | None = Field(
        default=None,
        ge=0.5,
        le=1.0,
        description="슬라이드 전환 감지 임계값",
    )


class ProcessVideoRequest(BaseModel):
    """비디오 처리 시작 요청"""

    sos_timestamps: list[float] = Field(
        default_factory=list,
        description="SOS 요청 타임스탬프 목록 (초)",
        examples=[[123.5, 456.2]],
    )
    options: ProcessingOptions | None = Field(
        default=None,
        description="처리 옵션 (미지정 시 기본값 사용)",
    )


# ==================== Note Requests ====================
# (현재 Note 관련 GET 요청은 path parameter만 사용하므로 별도 스키마 없음)
