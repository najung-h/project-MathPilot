import asyncio
import sys
from pathlib import Path

# backend 디렉토리를 모듈 검색 경로에 추가
sys.path.append(str(Path("backend").resolve()))

from app.utils.video_downloader import download_video

async def main():
    url = "https://www.youtube.com/watch?v=6sjt8_vbrzY&list=PLvbUC2Zh5oJty3nPh-MD1K2Nc9p82DoCt"
    output_dir = Path("downloads_test")
    
    print(f"Downloading video from: {url}")
    print(f"Output directory: {output_dir}")
    
    try:
        file_path = await download_video(url, output_dir)
        print(f"\n[SUCCESS] Video downloaded to: {file_path}")
        print(f"File exists: {file_path.exists()}")
        print(f"File size: {file_path.stat().st_size / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

