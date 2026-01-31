"""Local Storage Client - 로컬 파일 시스템 구현"""

import os
from pathlib import Path

from app.services.storage.base import BaseStorageClient


class LocalStorageClient(BaseStorageClient):
    """
    로컬 파일 시스템을 사용하는 스토리지 클라이언트

    개발 및 테스트 환경에서 사용
    """

    def __init__(self, storage_path: str, base_url: str):
        """
        Args:
            storage_path: 파일을 저장할 루트 디렉토리 경로
            base_url: 파일 URL 생성을 위한 base URL
        """
        self.storage_path = Path(storage_path)
        self.base_url = base_url.rstrip("/")

        # 스토리지 디렉토리 생성
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, key: str) -> Path:
        """키로부터 실제 파일 경로 생성"""
        return self.storage_path / key

    def _get_file_url(self, key: str) -> str:
        """키로부터 파일 URL 생성"""
        # URL 경로 구분자는 항상 /를 사용
        url_key = key.replace("\\", "/")
        return f"{self.base_url}/{url_key}"

    async def upload(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        파일 업로드

        Args:
            key: 저장 경로 (예: "videos/task-id/original.mp4")
            data: 파일 데이터
            content_type: MIME 타입 (로컬 저장에서는 사용하지 않음)

        Returns:
            업로드된 파일의 URL
        """
        file_path = self._get_file_path(key)

        # 상위 디렉토리 생성
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일 저장
        file_path.write_bytes(data)

        return self._get_file_url(key)

    async def download(self, key: str) -> bytes:
        """
        파일 다운로드

        Args:
            key: 파일 경로

        Returns:
            파일 데이터

        Raises:
            FileNotFoundError: 파일이 존재하지 않을 때
        """
        file_path = self._get_file_path(key)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {key}")

        return file_path.read_bytes()

    async def delete(self, key: str) -> None:
        """
        파일 삭제

        Args:
            key: 파일 경로
        """
        file_path = self._get_file_path(key)

        if file_path.exists():
            file_path.unlink()

    async def object_exists(self, key: str) -> bool:
        """
        객체 존재 여부 확인

        Args:
            key: 파일 경로

        Returns:
            존재 여부
        """
        file_path = self._get_file_path(key)
        return file_path.exists()

    async def generate_presigned_upload_url(
        self,
        key: str,
        content_type: str,
        expires_in: int = 3600,
    ) -> str:
        """
        Presigned Upload URL 생성

        로컬 스토리지에서는 일반 URL 반환
        실제로는 직접 업로드가 필요함

        Args:
            key: 업로드할 파일 경로
            content_type: MIME 타입
            expires_in: 만료 시간 (초) - 로컬에서는 사용하지 않음

        Returns:
            파일 URL (presigned URL이 아닌 일반 URL)
        """
        return self._get_file_url(key)

    async def generate_presigned_download_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """
        Presigned Download URL 생성

        로컬 스토리지에서는 일반 URL 반환

        Args:
            key: 다운로드할 파일 경로
            expires_in: 만료 시간 (초) - 로컬에서는 사용하지 않음

        Returns:
            파일 URL (presigned URL이 아닌 일반 URL)
        """
        return self._get_file_url(key)
