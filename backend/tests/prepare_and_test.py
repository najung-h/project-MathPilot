"""
Prepare Short Video & Run Test Pipeline
"""

import asyncio
import sys
import os
import shutil
from pathlib import Path
import ffmpeg

# backend 경로 추가
sys.path.append(str(Path("backend").resolve()))
from app.utils.video_downloader import download_video
from app.services.vision.frame_extractor import FrameExtractor
from app.services.vision.scene_detector import SceneDetector
from app.services.audio.audio_extractor import AudioExtractor
from app.services.audio.stt_processor import STTProcessor
from app.config import settings

# .env 로드
from dotenv import load_dotenv
load_dotenv(Path("backend/.env"))

OUTPUT_DIR = Path("downloads_test")
TARGET_URL = "https://www.youtube.com/watch?v=Woi45bzZCAQ&list=PLvbUC2Zh5oJty3nPh-MD1K2Nc9p82DoCt&index=13"
SHORT_VIDEO_NAME = "short_test.mp4"

async def prepare_short_video():
    # 파일이 이미 있으면 다운로드/자르기 스킵
    short_video_path = OUTPUT_DIR / SHORT_VIDEO_NAME
    if short_video_path.exists():
        print(f"[PREPARE] Using existing video: {short_video_path}")
        return short_video_path

    print(f"[PREPARE] Downloading video from: {TARGET_URL}")
    original_video_path = await download_video(TARGET_URL, OUTPUT_DIR)
    
    print(f"[PREPARE] Cutting first 5 minutes to: {short_video_path}")
    try:
        (
            ffmpeg
            .input(str(original_video_path), ss=0, t=300)
            .output(str(short_video_path), c="copy")
            .overwrite_output()
            .run(quiet=True)
        )
        return short_video_path
    except ffmpeg.Error as e:
        print(f"[ERROR] FFmpeg cut failed: {e.stderr.decode() if e.stderr else str(e)}")
        raise

async def run_pipeline_test(video_path: Path):
    print(f"\n[TEST] Running pipeline with: {video_path}")
    
    slides_dir = OUTPUT_DIR / "slides"
    if slides_dir.exists():
        shutil.rmtree(slides_dir)
    slides_dir.mkdir(exist_ok=True)

    # ==================== Vision Track ====================
    print("\n[Vision] 1. Extracting Frames (Interval: 1.0s)...")
    frame_extractor = FrameExtractor(interval_sec=1.0)
    
    # 프레임 추출 (메모리에만 저장)
    frames = await frame_extractor.extract_frames(video_path)
    print(f"  -> Extracted {len(frames)} frames.")
    
    if frames:
        print("\n[Vision] 2. Detecting Scenes (Slides)...")
        scene_detector = SceneDetector(ssim_threshold=0.85)
        slides = await scene_detector.detect_slides(frames)
        print(f"  -> Detected {len(slides)} unique slides.")
        
        # 슬라이드 저장
        print(f"  -> Saving detected slides to {slides_dir}...")
        for slide in slides:
            print(f"    - Slide {slide.slide_number}: {slide.timestamp_start:.1f}s ~ {slide.timestamp_end:.1f}s (SSIM: {slide.ssim_score})")
            if slide.frame.image_path: # 파일로 저장된 경우
                src_path = slide.frame.image_path
                dst_path = slides_dir / f"slide_{slide.slide_number:03d}_{slide.timestamp_start:.1f}s.jpg"
                shutil.copy2(src_path, dst_path)
            elif slide.frame.image_bytes: # 바이트인 경우
                import cv2
                import numpy as np
                nparr = np.frombuffer(slide.frame.image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                dst_path = slides_dir / f"slide_{slide.slide_number:03d}_{slide.timestamp_start:.1f}s.jpg"
                cv2.imwrite(str(dst_path), img)

    # ==================== Audio Track ====================
    print("\n[Audio] 1. Extracting Audio...")
    audio_extractor = AudioExtractor()
    audio_output_path = OUTPUT_DIR / "extracted_audio.wav"
    
    # 오디오 추출 (파일 있으면 스킵 가능하지만 빠르므로 수행)
    extracted_audio = await audio_extractor.extract_audio(
        video_path, 
        output_path=audio_output_path
    )
    
    # ==================== STT Track ====================
    if not settings.NVIDIA_API_KEY:
        print("\n[Audio] 2. STT Processing SKIPPED (No NVIDIA_API_KEY)")
    else:
        print("\n[Audio] 2. STT Processing (NVIDIA Riva)...")
        stt_processor = STTProcessor()
        
        try:
            transcript = await stt_processor.transcribe(audio_output_path)
            print(f"  -> STT Result:")
            print(f"    - Full Text Length: {len(transcript.full_text)}")
            print(f"    - Segments Count: {len(transcript.segments)}")
            
            # 디버깅: 세그먼트 일부 출력
            if transcript.segments:
                print("    - First 3 Segments:")
                for seg in transcript.segments[:3]:
                    print(f"      [{seg.start:.2f}s ~ {seg.end:.2f}s] {seg.text}")
            else:
                print("    [WARNING] No segments found! Timestamp mapping will fail.")
                
        except Exception as e:
            print(f"  -> STT Failed: {e}")

async def main():
    try:
        short_video_path = await prepare_short_video()
        await run_pipeline_test(short_video_path)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
