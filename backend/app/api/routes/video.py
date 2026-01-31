"""Video API routes - 영상 업로드 및 처리"""

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, UploadFile

from app.api.deps import StorageClientDep, SettingsDep
from app.schemas.requests import ProcessVideoRequest, VideoUrlRequest
from app.schemas.responses import (
    UploadResponse,
    ProcessVideoResponse,
    TaskStatusResponse,
    ProgressDetail,
)
from app.services.video_service import VideoProcessingService
from app.services.video_downloader import VideoDownloader

router = APIRouter()

# In-memory task storage (MVP용 - 추후 Redis/DB로 교체)
_task_store: dict[str, dict] = {}


async def download_and_process_url(
    task_id: str,
    url: str,
    sos_timestamps: list[float],
    task_store: dict,
    settings: any,
):
    """
    백그라운드 작업: URL 다운로드 -> 처리 시작
    """
    try:
        task = task_store[task_id]
        storage_path = Path(settings.STORAGE_PATH)
        video_dir = storage_path / "videos" / task_id
        
        # 1. 다운로드
        downloader = VideoDownloader(download_dir=video_dir)
        downloaded_path = await downloader.download_video(url, filename="original.mp4")
        
        # Task 정보 업데이트
        task["status"] = "processing" # 다운로드 완료 후 처리 중으로 변경
        task["s3_key"] = f"videos/{task_id}/original.mp4"
        task["filename"] = downloaded_path.name
        
        print(f"[{task_id}] Download completed. Starting processing...")

        # 2. 처리 시작
        await VideoProcessingService.process_video_task(
            task_id=task_id,
            task_store=task_store,
        )

    except Exception as e:
        print(f"[{task_id}] Error in download/process loop: {e}")
        import traceback
        traceback.print_exc()
        task_store[task_id]["status"] = "failed"
        task_store[task_id]["error_message"] = str(e)


@router.post("/fetch-url", response_model=ProcessVideoResponse)
async def fetch_video_url(
    request: VideoUrlRequest,
    background_tasks: BackgroundTasks,
    settings: SettingsDep,
):
    """URL에서 비디오 다운로드 및 처리 시작"""
    task_id = str(uuid.uuid4())
    
    # 초기 Task 생성
    _task_store[task_id] = {
        "status": "pending", # 다운로드 대기/진행 중
        "s3_key": None,
        "filename": request.url,
        "created_at": datetime.now(timezone.utc),
        "progress": {"vision": 0.0, "audio": 0.0, "synthesis": 0.0},
        "error_message": None,
        "sos_timestamps": request.sos_timestamps,
        "options": {
            "frame_interval_sec": settings.FRAME_INTERVAL_SEC,
            "ssim_threshold": settings.SSIM_THRESHOLD,
        }
    }

    # 백그라운드 작업 시작
    background_tasks.add_task(
        download_and_process_url,
        task_id=task_id,
        url=request.url,
        sos_timestamps=request.sos_timestamps,
        task_store=_task_store,
        settings=settings,
    )

    return ProcessVideoResponse(
        task_id=task_id,
        status="processing", # 클라이언트 입장에서는 처리가 시작된 것으로 간주
        estimated_time_sec=300, # 다운로드 포함 넉넉하게
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    storage: StorageClientDep,
    file: UploadFile = File(...),
):
    """비디오 파일 업로드 (Multipart)"""
    task_id = str(uuid.uuid4())
    # 파일 확장자 추출
    extension = file.filename.split(".")[-1] if file.filename else "mp4"
    file_key = f"videos/{task_id}/original.{extension}"

    # 파일 읽기 및 저장
    file_data = await file.read()
    file_url = await storage.upload(key=file_key, data=file_data, content_type=file.content_type or "video/mp4")

    # 태스크 초기화
    _task_store[task_id] = {
        "status": "uploaded",
        "s3_key": file_key, # 로컬에서는 파일 경로 키 역할
        "filename": file.filename,
        "created_at": datetime.now(timezone.utc),
        "progress": {"vision": 0.0, "audio": 0.0, "synthesis": 0.0},
        "error_message": None,
    }

    return UploadResponse(
        task_id=task_id,
        file_url=file_url,
        status="uploaded",
    )


@router.post("/{task_id}/process", response_model=ProcessVideoResponse)
async def process_video(
    task_id: str,
    request: ProcessVideoRequest,
    background_tasks: BackgroundTasks,
    settings: SettingsDep,
):
    """처리 시작 (BackgroundTasks)"""
    from app.core.exceptions import task_not_found_exception

    if task_id not in _task_store:
        raise task_not_found_exception(task_id)

    task = _task_store[task_id]
    task["status"] = "processing"
    task["sos_timestamps"] = request.sos_timestamps

    # 처리 옵션 병합 (요청 > 기본값)
    options = {
        "frame_interval_sec": (
            request.options.frame_interval_sec
            if request.options and request.options.frame_interval_sec
            else settings.FRAME_INTERVAL_SEC
        ),
        "ssim_threshold": (
            request.options.ssim_threshold
            if request.options and request.options.ssim_threshold
            else settings.SSIM_THRESHOLD
        ),
    }
    task["options"] = options

    # 백그라운드 처리 시작
    background_tasks.add_task(
        VideoProcessingService.process_video_task,
        task_id=task_id,
        task_store=_task_store,
    )

    # 추정 처리 시간 (임시값)
    estimated_time_sec = 120

    return ProcessVideoResponse(
        task_id=task_id,
        status="processing",
        estimated_time_sec=estimated_time_sec,
    )


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """처리 상태 조회"""
    from app.core.exceptions import task_not_found_exception

    if task_id not in _task_store:
        raise task_not_found_exception(task_id)

    task = _task_store[task_id]

    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=ProgressDetail(**task["progress"]),
        error_message=task.get("error_message"),
    )
