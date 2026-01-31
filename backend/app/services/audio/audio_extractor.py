"""Audio Extractor - 비디오에서 오디오 추출"""

from dataclasses import dataclass
from pathlib import Path
import ffmpeg


@dataclass
class ExtractedAudio:
    """추출된 오디오 정보"""

    audio_path: Path | None = None
    audio_bytes: bytes | None = None
    duration_sec: float = 0.0
    sample_rate: int = 16000
    format: str = "wav"


class AudioExtractor:
    """
    비디오에서 오디오 트랙 추출
    FFmpeg 사용
    """

    def __init__(
        self,
        output_format: str = "wav",
        sample_rate: int = 16000,
    ):
        """
        Args:
            output_format: 출력 오디오 포맷 (wav, mp3 등)
            sample_rate: 샘플링 레이트 (Whisper는 16kHz 권장)
        """
        self.output_format = output_format
        self.sample_rate = sample_rate

    async def extract_audio(
        self,
        video_path: str | Path,
        output_path: str | Path | None = None,
    ) -> ExtractedAudio:
        """
        비디오에서 오디오 추출

        Args:
            video_path: 비디오 파일 경로
            output_path: 오디오 저장 경로 (None이면 bytes로 반환 시도하지만 FFmpeg 특성상 파일 저장이 안정적)

        Returns:
            추출된 오디오 정보
        """
        video_path = str(video_path)
        
        # Duration 정보 얻기
        try:
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
        except Exception:
            duration = 0.0

        if output_path:
            output_path = str(output_path)
            try:
                (
                    ffmpeg
                    .input(video_path)
                    .output(
                        output_path,
                        acodec='pcm_s16le', # WAV 코덱
                        ac=1,               # Mono
                        ar=self.sample_rate # 16kHz
                    )
                    .overwrite_output()
                    .run(quiet=True)
                )
                
                return ExtractedAudio(
                    audio_path=Path(output_path),
                    duration_sec=duration,
                    sample_rate=self.sample_rate,
                    format=self.output_format
                )
            except ffmpeg.Error as e:
                raise RuntimeError(f"FFmpeg audio extraction failed: {e.stderr.decode() if e.stderr else str(e)}")

        else:
            # Bytes로 반환 (pipe 사용)
            try:
                out, _ = (
                    ffmpeg
                    .input(video_path)
                    .output(
                        'pipe:',
                        format='wav',
                        acodec='pcm_s16le',
                        ac=1,
                        ar=self.sample_rate
                    )
                    .run(capture_stdout=True, capture_stderr=True)
                )
                
                return ExtractedAudio(
                    audio_bytes=out,
                    duration_sec=duration,
                    sample_rate=self.sample_rate,
                    format="wav"
                )
            except ffmpeg.Error as e:
                raise RuntimeError(f"FFmpeg audio extraction failed: {e.stderr.decode() if e.stderr else str(e)}")

    async def extract_audio_from_bytes(
        self,
        video_bytes: bytes,
    ) -> ExtractedAudio:
        """
        바이트 데이터에서 오디오 추출
        """
        import tempfile
        import os

        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video:
            temp_video.write(video_bytes)
            temp_video_path = temp_video.name

        try:
            # pipe로 바이트 반환
            return await self.extract_audio(temp_video_path)
        finally:
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)