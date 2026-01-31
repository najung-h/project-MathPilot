"""Video Processing Service - 전체 파이프라인 오케스트레이션"""

import asyncio
import os
from pathlib import Path
from typing import Any

from app.config import get_settings
from app.api.deps import get_llm_client, get_storage_client

# Service Modules
from app.services.vision.frame_extractor import FrameExtractor
from app.services.vision.scene_detector import SceneDetector
from app.services.vision.ocr_processor import OCRProcessor
from app.services.audio.audio_extractor import AudioExtractor
from app.services.audio.stt_processor import STTProcessor
from app.services.synthesis.segment_mapper import SegmentMapper
from app.services.synthesis.note_generator import NoteGenerator


class VideoProcessingService:
    """비디오 처리 전체 파이프라인을 관리하는 서비스"""

    @staticmethod
    async def process_video_task(
        task_id: str,
        task_store: dict[str, Any],
    ) -> None:
        """
        백그라운드에서 비디오 처리 파이프라인 실행
        """
        # 최신 설정 가져오기 (테스트 환경에서 변경된 설정 반영)
        settings = get_settings()
        
        task = task_store[task_id]
        storage_path = Path(settings.STORAGE_PATH)
        video_key = task["s3_key"]
        
        # 로컬 파일 경로 확인
        # LocalStorageClient를 가정하므로 s3_key가 곧 상대 경로
        video_path = storage_path / video_key
        
        # 중간 결과 저장 경로
        process_dir = storage_path / "processing" / task_id
        process_dir.mkdir(parents=True, exist_ok=True)
        
        frames_dir = process_dir / "frames"
        slides_dir = process_dir / "slides"
        frames_dir.mkdir(exist_ok=True)
        slides_dir.mkdir(exist_ok=True)

        try:
            # 의존성 객체 생성 (여기서는 함수 내부에서 생성하지만, 실제로는 DI를 활용하는 것이 좋음)
            # LLM Client는 API 의존성 함수를 활용해 생성
            llm_client = get_llm_client(settings)
            
            # ==================== Phase 1: Pre-processing (병렬) ====================
            # 비디오 길이 미리 파악 (타임스탬프 보정용)
            extractor = AudioExtractor()
            audio_info = await extractor.extract_audio(video_path)
            video_duration = audio_info.duration_sec

            vision_task = asyncio.create_task(
                VideoProcessingService._process_vision(
                    task_id, task, video_path, frames_dir, slides_dir, llm_client, video_duration
                )
            )
            audio_task = asyncio.create_task(
                VideoProcessingService._process_audio(
                    task_id, task, video_path, process_dir
                )
            )

            vision_result, audio_result = await asyncio.gather(
                vision_task, audio_task
            )

            # Vision, Audio 처리 완료 - synthesis는 별도 요청으로 처리
            task["status"] = "ready_for_synthesis"  # 요약 준비 완료
            task["vision_result"] = vision_result
            task["audio_result"] = audio_result
            task["progress"]["vision"] = 1.0
            task["progress"]["audio"] = 1.0
            print(f"[{task_id}] Vision and Audio processing completed. Ready for synthesis.")

        except Exception as e:
            import traceback
            traceback.print_exc()
            task["status"] = "failed"
            task["error_message"] = str(e)

    @staticmethod
    async def run_synthesis_task(
        task_id: str,
        task_store: dict[str, Any],
    ) -> None:
        """
        Synthesis 단계만 실행 (강의 요약 생성)
        """
        settings = get_settings()
        task = task_store[task_id]
        storage_path = Path(settings.STORAGE_PATH)
        
        try:
            if task["status"] != "ready_for_synthesis":
                raise ValueError(f"Task {task_id} is not ready for synthesis. Current status: {task['status']}")
            
            task["status"] = "generating_summary"
            
            # 저장된 vision/audio 결과 가져오기
            vision_result = task.get("vision_result")
            audio_result = task.get("audio_result")
            
            if not vision_result or not audio_result:
                raise ValueError("Vision or Audio result not found")
            
            # LLM 클라이언트 생성
            llm_client = get_llm_client(settings)
            
            # slides_dir 경로
            process_dir = storage_path / "processing" / task_id
            slides_dir = process_dir / "slides"
            
            # Synthesis 실행
            await VideoProcessingService._process_synthesis(
                task_id, task, vision_result, audio_result, llm_client, slides_dir, storage_path
            )
            
            # 완료
            task["status"] = "completed"
            task["progress"]["synthesis"] = 1.0
            print(f"[{task_id}] Synthesis completed.")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            task["status"] = "failed"
            task["error_message"] = str(e)

    @staticmethod
    async def _process_vision(
        task_id: str,
        task: dict[str, Any],
        video_path: Path,
        frames_dir: Path,
        slides_dir: Path,
        llm_client: Any,
        video_duration: float | None = None,
    ) -> dict[str, Any]:
        """Vision Pipeline"""
        print(f"[{task_id}] Vision Pipeline Start")
        settings = get_settings()
        
        # 1. Frame Extraction
        extractor = FrameExtractor(interval_sec=settings.FRAME_INTERVAL_SEC)
        frames = await extractor.extract_frames(video_path, output_dir=frames_dir)
        task["progress"]["vision"] = 0.3
        
        # 2. Scene Detection
        detector = SceneDetector(ssim_threshold=settings.SSIM_THRESHOLD)
        slides = await detector.detect_slides(frames, video_duration=video_duration)
        task["progress"]["vision"] = 0.6
        
        # 3. OCR Processing
        ocr_processor = OCRProcessor(llm_client)
        
        # 슬라이드 이미지를 바이트로 로드
        slide_images = []
        import cv2
        for slide in slides:
            # 대표 프레임 이미지 경로
            if slide.frame.image_path:
                # 슬라이드별 디렉토리에 복사 (선택 사항)
                slide_filename = f"slide_{slide.slide_number:03d}.jpg"
                dst_path = slides_dir / slide_filename
                
                # OpenCV로 읽어서 다시 저장 (포맷 통일)
                img = cv2.imread(str(slide.frame.image_path))
                cv2.imwrite(str(dst_path), img)
                
                with open(dst_path, "rb") as f:
                    slide_images.append(f.read())
            else:
                # 메모리에만 있는 경우 (현재는 파일 저장 모드라 이쪽으로 안 옴)
                slide_images.append(slide.frame.image_bytes)

        ocr_results = await ocr_processor.process_slides(slides, slide_images)
        task["progress"]["vision"] = 1.0
        
        return {
            "slides": slides,
            "ocr_results": ocr_results,
        }

    @staticmethod
    async def _process_audio(
        task_id: str,
        task: dict[str, Any],
        video_path: Path,
        process_dir: Path,
    ) -> dict[str, Any]:
        """Audio Pipeline"""
        print(f"[{task_id}] Audio Pipeline Start")
        settings = get_settings()
        
        # 1. Audio Extraction
        extractor = AudioExtractor()
        audio_path = process_dir / "audio.wav"
        audio_info = await extractor.extract_audio(video_path, output_path=audio_path)
        print(f"[{task_id}] Audio extracted: {audio_path}, duration: {audio_info.duration_sec}s")
        task["progress"]["audio"] = 0.5
        
        # 2. STT Processing
        stt_processor = STTProcessor()
        print(f"[{task_id}] NVIDIA_API_KEY present: {bool(settings.NVIDIA_API_KEY)}")
        if settings.NVIDIA_API_KEY:
            print(f"[{task_id}] Starting STT with Nvidia API...")
            transcript_result = await stt_processor.transcribe(audio_path)
            print(f"[{task_id}] STT completed: {len(transcript_result.segments)} segments, full_text length: {len(transcript_result.full_text)}")
        else:
            # API 키 없으면 빈 결과
            print(f"[{task_id}] WARNING: No NVIDIA_API_KEY, returning empty transcript")
            from app.services.audio.stt_processor import TranscriptResult
            transcript_result = TranscriptResult("", [], "ko-KR", 0.0)
            
        task["progress"]["audio"] = 1.0
        
        return {
            "transcript_result": transcript_result
        }

    @staticmethod
    async def _process_synthesis(
        task_id: str,
        task: dict[str, Any],
        vision_result: dict[str, Any],
        audio_result: dict[str, Any],
        llm_client: Any,
        slides_dir: Path,
        storage_path: Path,
    ) -> None:
        """Synthesis Pipeline"""
        print(f"[{task_id}] Synthesis Pipeline Start")
        settings = get_settings()
        task["progress"]["synthesis"] = 0.1
        
        slides = vision_result["slides"]
        ocr_results = vision_result["ocr_results"]
        transcript_result = audio_result["transcript_result"]
        
        # 디버깅: STT 결과 확인
        print(f"[{task_id}] Total transcript segments: {len(transcript_result.segments)}")
        print(f"[{task_id}] Full transcript text length: {len(transcript_result.full_text)}")
        if len(transcript_result.segments) > 0:
            print(f"[{task_id}] First segment: start={transcript_result.segments[0].start}, end={transcript_result.segments[0].end}, text='{transcript_result.segments[0].text[:100]}'")
        else:
            print(f"[{task_id}] WARNING: No transcript segments found!")
        
        # 1. Segment Mapping
        mapper = SegmentMapper(padding_sec=settings.AUDIO_PADDING_SEC)
        segments = mapper.map_segments(
            slides,
            ocr_results,
            transcript_result.segments,
            sos_timestamps=task.get("sos_timestamps")
        )
        task["progress"]["synthesis"] = 0.3
        
        # 2. Note Generation
        generator = NoteGenerator(llm_client)
        
        # 슬라이드 이미지 키 목록 생성 (상대 경로)
        slide_image_keys = [
            str(Path("processing") / task_id / "slides" / f"slide_{s.slide_number:03d}.jpg").replace("\\", "/")
            for s in slides
        ]
        
        note = await generator.generate_note(
            segments,
            slide_image_keys,
            title=task.get("filename", "Lecture Note")
        )
        
        # 3. 결과 저장
        output_dir = storage_path / "outputs" / task_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 마크다운 파일 저장
        with open(output_dir / "note.md", "w", encoding="utf-8") as f:
            f.write(note.markdown_content)
            
        # 4. 전체 대본(Transcript) JSON 저장
        import json
        transcript_data = {
            "full_text": transcript_result.full_text,
            "segments": [
                {
                    "start": s.start,
                    "end": s.end,
                    "text": s.text
                }
                for s in transcript_result.segments
            ]
        }
        with open(output_dir / "transcript.json", "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, ensure_ascii=False, indent=2)

        # JSON 데이터 저장 (필요 시)
        
        # Task 업데이트
        task["note_data"] = {
            "title": note.title,
            "slides": [
                {
                    "slide_number": s.slide_number,
                    "timestamp_start": s.timestamp_start,
                    "timestamp_end": s.timestamp_end,
                    "image_s3_key": s.image_s3_key,
                    "ocr_content": segments[i].ocr_content,  # OCR 원본 (수식)
                    "audio_summary": s.summary_content,  # LLM 생성 요약
                    "raw_transcript": segments[i].audio_transcript,  # STT 원본 전사
                    "sos_explanation": s.sos_explanation,
                }
                for i, s in enumerate(note.slides)
            ]
        }
        task["progress"]["synthesis"] = 1.0
