"""
Vision & Audio Pipeline Module Test
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# backend 경로 추가
sys.path.append(str(Path("backend").resolve()))

# .env 로드
load_dotenv(Path("backend/.env"))

from app.services.vision.frame_extractor import FrameExtractor
from app.services.vision.scene_detector import SceneDetector
from app.services.audio.audio_extractor import AudioExtractor
from app.services.audio.stt_processor import STTProcessor
from app.config import settings

async def test_pipeline():
    # 1. 테스트 비디오 경로 설정
    # 아까 다운로드 받은 파일 찾기
    download_dir = Path("downloads_test")
    video_files = list(download_dir.glob("*.mp4"))
    
    if not video_files:
        print("[ERROR] No video file found in downloads_test/")
        return
    
    video_path = video_files[0]
    print(f"[INPUT] Video: {video_path}")

    # ==================== Vision Track ====================
    print("\n[Vision] 1. Extracting Frames...")
    frame_extractor = FrameExtractor(interval_sec=1.0)
    
    # 프레임 추출 (메모리 방식)
    frames = await frame_extractor.extract_frames(video_path)
    print(f"  -> Extracted {len(frames)} frames.")
    
    if frames:
        print("\n[Vision] 2. Detecting Scenes (Slides)...")
        scene_detector = SceneDetector(ssim_threshold=0.85)
        slides = await scene_detector.detect_slides(frames)
        print(f"  -> Detected {len(slides)} unique slides.")
        
        # 첫 번째 슬라이드 정보 출력
        if slides:
            print(f"  -> First Slide: {slides[0].timestamp_start}s ~ {slides[0].timestamp_end}s")

    # ==================== Audio Track ====================
    print("\n[Audio] 1. Extracting Audio...")
    audio_extractor = AudioExtractor()
    audio_output_path = download_dir / "extracted_audio.wav"
    
    extracted_audio = await audio_extractor.extract_audio(
        video_path, 
        output_path=audio_output_path
    )
    print(f"  -> Audio extracted to: {extracted_audio.audio_path}")
    print(f"  -> Duration: {extracted_audio.duration_sec}s")
    
    # ==================== STT Track (API Key Check) ====================
    if not settings.NVIDIA_API_KEY:
        print("\n[Audio] 2. STT Processing SKIPPED (No NVIDIA_API_KEY)")
    else:
        print("\n[Audio] 2. STT Processing (NVIDIA Riva)...")
        stt_processor = STTProcessor()
        
        try:
            transcript = await stt_processor.transcribe(audio_output_path)
            print(f"  -> STT Success!")
            print(f"  -> Full Text Length: {len(transcript.full_text)} chars")
            print(f"  -> First Segment: {transcript.segments[0].text if transcript.segments else 'None'}")
        except Exception as e:
            print(f"  -> STT Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_pipeline())
