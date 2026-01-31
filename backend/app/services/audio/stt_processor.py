import os
import asyncio
from dataclasses import dataclass
from pathlib import Path

# Riva client는 선택적 의존성으로 처리 (NVIDIA Cloud 환경에서만 사용)
try:
    import riva.client
    RIVA_AVAILABLE = True
except ImportError:
    RIVA_AVAILABLE = False
    riva = None  # type: ignore

from app.config import settings

@dataclass
class TranscriptSegment:
    start: float
    end: float
    text: str

@dataclass
class TranscriptResult:
    full_text: str
    segments: list[TranscriptSegment]
    language: str
    duration_sec: float

class STTProcessor:
    def __init__(self):
        if not RIVA_AVAILABLE:
            print("[Warning] NVIDIA Riva client not available. STT will be disabled.")
            self.auth = None
            self.asr_service = None
            self.config = None
            return
            
        # 1. NVIDIA Riva 서버 연결 (gRPC)
        self.auth = riva.client.Auth(
            None,
            use_ssl=True,
            uri="grpc.nvcf.nvidia.com:443",
            metadata_args=[
                ("function-id", "b702f636-f60c-4a3d-a6f4-f3568c13bd7d"), # Whisper Large v3
                ("authorization", f"Bearer {settings.NVIDIA_API_KEY}")
            ]
        )
        self.asr_service = riva.client.ASRService(self.auth)
        
        # 2. 모델 설정 (Offline 모드 + 타임스탬프 ON)
        self.config = riva.client.RecognitionConfig(
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            sample_rate_hertz=16000,        # ★ 입력 오디오 16kHz 필수
            language_code="ko-KR",          # 한국어
            max_alternatives=1,
            enable_automatic_punctuation=True,
            verbatim_transcripts=False,
            enable_word_time_offsets=True   # ★ 타임스탬프 필수 옵션
        )

    async def transcribe(self, audio_path: str | Path) -> TranscriptResult:
        if not RIVA_AVAILABLE or self.asr_service is None:
            # Riva가 없으면 빈 결과 반환
            return TranscriptResult(
                full_text="[STT unavailable - Riva client not installed]",
                segments=[],
                language="ko-KR",
                duration_sec=0.0
            )
            
        audio_path = Path(audio_path)
        
        # 3. 파일 읽기 (바이너리)
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        print(f"[Riva] Sending {len(audio_bytes)} bytes to server...")

        # 4. Riva 서버로 전송 (Blocking 방지를 위해 스레드로 실행)
        # offline_recognize는 gRPC를 통해 대용량 파일도 안정적으로 처리함
        try:
            response = await asyncio.to_thread(
                self.asr_service.offline_recognize, 
                audio_bytes, 
                self.config
            )
        except Exception as e:
            print(f"[Riva Error] {str(e)}")
            raise

        # 5. 결과 파싱
        full_text = ""
        segments = []
        
        if not response.results:
            return TranscriptResult("", [], "ko-KR", 0.0)

        for result in response.results:
            if not result.alternatives: continue
            
            alt = result.alternatives[0]
            text_chunk = alt.transcript
            full_text += text_chunk + " "

            # 타임스탬프 추출 (ms -> sec 변환)
            if alt.words:
                start = alt.words[0].start_time / 1000.0
                end = alt.words[-1].end_time / 1000.0
                segments.append(TranscriptSegment(start, end, text_chunk.strip()))
            else:
                # words가 없으면 전체 구간을 하나의 세그먼트로 처리
                print(f"[Riva Warning] No word timestamps for result, creating single segment")
                # 임시로 0부터 시작하는 큰 세그먼트 생성
                segments.append(TranscriptSegment(0.0, 999999.0, text_chunk.strip()))

        # 세그먼트가 여전히 비어있으면 전체 텍스트로 하나의 큰 세그먼트 생성
        if not segments and full_text.strip():
            print(f"[Riva Warning] No segments created, creating one large segment for entire transcript")
            segments.append(TranscriptSegment(0.0, 999999.0, full_text.strip()))

        duration = segments[-1].end if segments else 0.0
        
        return TranscriptResult(
            full_text=full_text.strip(),
            segments=segments,
            language="ko-KR",
            duration_sec=duration
        )