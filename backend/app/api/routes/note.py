"""Note API routes - 노트 조회 및 다운로드"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from app.api.deps import StorageClientDep, SettingsDep
from app.schemas.responses import (
    NoteResponse,
    NoteDownloadResponse,
    SlideImageResponse,
    SlideDetail,
)

router = APIRouter()

# video.py와 공유하는 task store (MVP용)
from app.api.routes.video import _task_store


@router.get("/{task_id}", response_model=NoteResponse)
async def get_note(
    task_id: str,
    storage: StorageClientDep,
    settings: SettingsDep,
):
    """생성된 노트 조회 (JSON) - ready_for_synthesis 상태에서도 원본 데이터 제공"""
    from app.core.exceptions import task_not_found_exception

    if task_id not in _task_store:
        raise task_not_found_exception(task_id)

    task = _task_store[task_id]

    # completed 상태 - 완전한 노트 반환
    if task["status"] == "completed":
        note_data = task.get("note_data", {})

        # 슬라이드 이미지 URL 생성
        slides = []
        for slide in note_data.get("slides", []):
            image_url = await storage.generate_presigned_download_url(
                key=slide["image_s3_key"],
                expires_in=settings.S3_PRESIGNED_URL_EXPIRY,
            )
            slides.append(
                SlideDetail(
                    slide_number=slide["slide_number"],
                    timestamp_start=slide["timestamp_start"],
                    timestamp_end=slide["timestamp_end"],
                    image_url=image_url,
                    ocr_content=slide["ocr_content"],
                    audio_summary=slide["audio_summary"],
                    raw_transcript=slide.get("raw_transcript", ""),
                    sos_explanation=slide.get("sos_explanation"),
                )
            )

        return NoteResponse(
            task_id=task_id,
            title=note_data.get("title", "Untitled Note"),
            slides=slides,
            created_at=task["created_at"],
        )
    
    # ready_for_synthesis 또는 generating_summary 상태 - 원본 데이터만 반환
    elif task["status"] in ["ready_for_synthesis", "generating_summary"]:
        vision_result = task.get("vision_result", {})
        audio_result = task.get("audio_result", {})
        
        slides_data = vision_result.get("slides", [])
        ocr_results = vision_result.get("ocr_results", [])
        transcript_result = audio_result.get("transcript_result")
        
        if not slides_data or not transcript_result:
            raise task_not_found_exception(task_id)
        
        # 세그먼트 매핑 (간단 버전)
        from app.services.synthesis.segment_mapper import SegmentMapper
        mapper = SegmentMapper(padding_sec=settings.AUDIO_PADDING_SEC)
        segments = mapper.map_segments(
            slides_data,
            ocr_results,
            transcript_result.segments,
            sos_timestamps=None
        )
        
        slides = []
        for i, (slide, segment) in enumerate(zip(slides_data, segments)):
            # 슬라이드 이미지 URL
            slide_image_key = f"processing/{task_id}/slides/slide_{slide.slide_number:03d}.jpg"
            image_url = await storage.generate_presigned_download_url(
                key=slide_image_key,
                expires_in=settings.S3_PRESIGNED_URL_EXPIRY,
            )
            
            slides.append(
                SlideDetail(
                    slide_number=slide.slide_number,
                    timestamp_start=slide.timestamp_start,
                    timestamp_end=slide.timestamp_end,
                    image_url=image_url,
                    ocr_content=segment.ocr_content,
                    audio_summary="요약 생성 중...",  # 아직 생성 안 됨
                    raw_transcript=segment.audio_transcript,
                    sos_explanation=None,
                )
            )
        
        return NoteResponse(
            task_id=task_id,
            title=task.get("filename", "Lecture Note"),
            slides=slides,
            created_at=task["created_at"],
        )
    
    else:
        raise task_not_found_exception(task_id)


@router.get("/{task_id}/download", response_model=NoteDownloadResponse)
async def download_note(
    task_id: str,
    storage: StorageClientDep,
    settings: SettingsDep,
):
    """마크다운 파일 다운로드 URL"""
    from app.core.exceptions import task_not_found_exception

    if task_id not in _task_store:
        raise task_not_found_exception(task_id)

    task = _task_store[task_id]

    if task["status"] != "completed":
        raise task_not_found_exception(task_id)

    s3_key = f"outputs/{task_id}/note.md"
    download_url = await storage.generate_presigned_download_url(
        key=s3_key,
        expires_in=settings.S3_PRESIGNED_URL_EXPIRY,
    )

    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.S3_PRESIGNED_URL_EXPIRY
    )

    return NoteDownloadResponse(
        download_url=download_url,
        filename=f"note_{task_id}.md",
        expires_at=expires_at,
    )


@router.get("/{task_id}/slides/{slide_number}/image", response_model=SlideImageResponse)
async def get_slide_image(
    task_id: str,
    slide_number: int,
    storage: StorageClientDep,
    settings: SettingsDep,
):
    """특정 슬라이드 이미지 URL"""
    from app.core.exceptions import task_not_found_exception

    if task_id not in _task_store:
        raise task_not_found_exception(task_id)

    s3_key = f"processing/{task_id}/slides/slide_{slide_number:03d}.jpg"
    image_url = await storage.generate_presigned_download_url(
        key=s3_key,
        expires_in=settings.S3_PRESIGNED_URL_EXPIRY,
    )

    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.S3_PRESIGNED_URL_EXPIRY
    )

    return SlideImageResponse(
        image_url=image_url,
        expires_at=expires_at,
    )
