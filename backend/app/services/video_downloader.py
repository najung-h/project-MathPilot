"""Video Downloader Service"""

import asyncio
from pathlib import Path
from typing import Any

import yt_dlp
from app.core.exceptions import VideoProcessingError


class VideoDownloader:
    """
    YouTube 등 외부 URL에서 비디오를 다운로드하는 서비스
    yt-dlp 라이브러리 사용
    """

    def __init__(self, download_dir: str | Path):
        """
        Args:
            download_dir: 파일 저장 디렉토리
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    async def download_video(self, url: str, filename: str | None = None) -> Path:
        """
        비디오 다운로드 실행

        Args:
            url: 비디오 URL
            filename: 저장할 파일명 (확장자 포함). None이면 yt-dlp 기본값 사용.

        Returns:
            다운로드된 파일의 절대 경로
        """
        # yt-dlp 옵션 설정
        ydl_opts: dict[str, Any] = {
            "format": "bv*+ba/b",  # 최고 화질
            "merge_output_format": "mp4",
            "outtmpl": str(self.download_dir / "%(title)s [%(id)s].%(ext)s"),
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            # FFmpeg가 설치되어 있어야 함
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4",
            }],
        }

        if filename:
            ydl_opts["outtmpl"] = str(self.download_dir / filename)

        try:
            # yt-dlp는 동기 함수이므로 스레드 풀에서 실행
            return await asyncio.to_thread(self._run_download, url, ydl_opts)
        except Exception as e:
            raise VideoProcessingError(f"Video download failed: {str(e)}")

    def _run_download(self, url: str, ydl_opts: dict[str, Any]) -> Path:
        """yt-dlp 실행 (동기 함수)"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 메타데이터 추출
            info = ydl.extract_info(url, download=True)
            
            if "requested_downloads" in info:
                # 다운로드된 파일 경로 반환
                downloaded_file = info["requested_downloads"][0]["filepath"]
            else:
                # 이미 다운로드되어 있거나 직접 경로 추론
                filename = ydl.prepare_filename(info)
                # 확장자가 다를 수 있으므로 확인 (merging 등으로 변경될 수 있음)
                # 여기서는 간단히 prepare_filename 결과 사용하되, mp4로 강제 변환되었음을 가정
                downloaded_file = filename
                
                # 병합된 파일명 보정 (mp4로 변경된 경우)
                p = Path(downloaded_file)
                if p.suffix != ".mp4":
                     mp4_path = p.with_suffix(".mp4")
                     if mp4_path.exists():
                         downloaded_file = str(mp4_path)

            return Path(downloaded_file)
