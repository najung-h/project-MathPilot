# Backend Implementation Flow Analysis

이 문서는 현재 구현된 백엔드 시스템의 코드 흐름을 분석하고, 초기 기획 문서(`IMPLEMENTATION_PLAN.md`, `1600_구조 초안 작업내역.md`)와 대조하여 현황을 정리한 보고서입니다.

---

## 1. 전체 파이프라인 개요 (Architecture Overview)

현재 백엔드는 **FastAPI**를 기반으로 하며, **Vision(시각)**과 **Audio(청각)** 처리를 비동기 병렬(`asyncio.gather`)로 수행한 후, 이를 **Synthesis(융합)**하여 최종 마크다운 노트를 생성하는 구조입니다.

### 🛠 실행 흐름 (Execution Flow)

1.  **User Upload**: 사용자가 비디오 파일 업로드 → `Task ID` 생성 및 파일 저장 (`local` storage).
2.  **Processing Start**: `/process` API 호출 → 백그라운드 작업(`BackgroundTasks`) 시작.
3.  **Parallel Tracks**:
    *   **Track A (Vision)**: `Frame Extraction` → `Scene Detection` (SSIM) → `OCR` (NVIDIA Vision LLM).
    *   **Track B (Audio)**: `Audio Extraction` (FFmpeg) → `STT` (NVIDIA Riva gRPC).
4.  **Synthesis**: Vision 결과(슬라이드+텍스트)와 Audio 결과(전사+타임스탬프)를 매핑 → LLM(NVIDIA NIM)으로 요약 및 마크다운 생성.
5.  **Output**: 최종 `note.md` 파일 생성 및 저장.

---

## 2. 모듈별 상세 구현 분석 (Detailed Analysis)

### 2.1 Service Orchestration (`video_service.py`)
*   **역할**: 전체 파이프라인의 지휘자.
*   **구현 내용**:
    *   `process_video_task`: 메인 진입점. `_process_vision`과 `_process_audio`를 `asyncio.gather`로 병렬 실행.
    *   에러 핸들링: 각 단계별 예외를 포착하고 Task 상태를 업데이트.
*   **특이사항**: 로컬 스토리지 경로(`storage/`)를 기반으로 동작하며, 클라우드(S3) 확장성을 염두에 둔 `s3_key` 변수명을 사용 중.

### 2.2 Vision Pipeline (`services/vision/`)
*   **`frame_extractor.py`**:
    *   OpenCV를 사용하여 설정된 간격(기본 1초)으로 프레임 이미지 추출.
*   **`scene_detector.py`**:
    *   **SSIM(구조적 유사도)** 알고리즘을 사용해 이전 프레임과 비교.
    *   유사도가 임계값(`0.85`)보다 낮으면 "새로운 슬라이드"로 판단.
    *   **현황**: 마지막 슬라이드의 종료 시간(`timestamp_end`) 처리가 다소 단순화(마지막 프레임 시간)되어 있음.
*   **`ocr_processor.py`**:
    *   NVIDIA Vision LLM (`meta/llama-3.2-90b-vision-instruct`)을 사용하여 슬라이드 이미지에서 텍스트와 수식($\LaTeX$) 추출.
    *   시스템 프롬프트를 통해 마크다운 구조화를 강제함.

### 2.3 Audio Pipeline (`services/audio/`)
*   **`audio_extractor.py`**:
    *   FFmpeg를 사용하여 비디오에서 오디오를 추출.
    *   **중요**: Riva STT를 위해 **16000Hz, Mono, PCM(WAV)** 포맷으로 강제 변환 (안정성 확보).
*   **`stt_processor.py`**:
    *   **기술 변경**: 초기 기획(Whisper API) → 구현(NVIDIA Riva gRPC)으로 변경.
    *   **이유**: 대용량 오디오 전송 시 HTTP 연결 끊김 문제 해결 및 정확한 타임스탬프(`enable_word_time_offsets`) 확보를 위함.
    *   **현황**: gRPC 프로토콜을 사용하여 매우 안정적으로 동작함.

### 2.4 Synthesis Pipeline (`services/synthesis/`)
*   **`segment_mapper.py`**:
    *   슬라이드의 타임스탬프 구간에 해당하는 오디오 텍스트를 매핑.
    *   싱크 오차를 줄이기 위해 앞뒤 패딩(`padding_sec`) 적용.
*   **`note_generator.py`**:
    *   매핑된 데이터(이미지+OCR+음성)를 LLM에 전달하여 최종 요약 생성.
    *   **SOS 기능**: 사용자가 요청한 구간(`sos_timestamps`)에 대해 심층 해설 생성 로직 구현됨.

---

## 3. 기획 문서와의 대조 (Plan vs. Implementation)

| 항목 | 초기 계획 (`IMPLEMENTATION_PLAN.md`) | 실제 구현 (Current Status) | 비고 |
| :--- | :--- | :--- | :--- |
| **STT 모델** | OpenAI Whisper API | **NVIDIA Riva (gRPC)** | 안정성 및 성능 문제로 변경 (성공적) |
| **OCR 모델** | GPT-4o / Gemini Vision | **NVIDIA NIM (Llama 3.2 Vision)** | NVIDIA 스택 통일 (비용/성능 최적화) |
| **저장소** | AWS S3 | **Local File System** | 개발 편의성을 위해 로컬로 구현 (인터페이스는 S3 호환 가능) |
| **타임스탬프** | 정확한 구간 매핑 | **Riva Word Timestamps 활용** | Riva의 단어 단위 타임스탬프를 가공하여 문장 구간 생성 |
| **프론트엔드** | React | **미구현** | 백엔드 API만 완성된 상태 |
| **Task 관리** | DB 연동 | **In-memory (Dict)** | 서버 재시작 시 데이터 휘발 (MVP 한계) |

---

## 4. 종합 평가 및 제언

### ✅ 완료된 사항 (Completed)
*   **Core Backend Logic**: 비디오 업로드부터 노트 생성까지의 전 과정이 끊김 없이 동작합니다.
*   **High Stability**: gRPC 도입으로 오디오 처리의 안정성이 크게 향상되었습니다.
*   **Parallel Processing**: Vision과 Audio가 동시에 처리되어 전체 작업 시간을 단축했습니다.
*   **Testing**: `test_service_integration.py`를 통해 실제 파일을 이용한 E2E 테스트가 검증되었습니다.

### 🚧 향후 개선 과제 (To-Do / Improvements)
1.  **Frontend 개발**: 현재 API만 존재하므로, 사용자 UI(React 등) 개발이 시급합니다.
2.  **Persistence (DB 도입)**: `_task_store`를 Redis나 PostgreSQL로 교체하여 데이터 영속성을 확보해야 합니다.
4.  **Error Handling**: Riva 연결 실패나 LLM 응답 지연 시의 재시도(Retry) 로직을 더 견고하게 다듬을 수 있습니다.

---

**결론**: 백엔드 시스템은 **기능적으로 완성**되었으며, 실제 서비스 가능한 수준의 코어 로직을 갖추고 있습니다. 기획 의도였던 "단권화 노트 자동 생성"을 성공적으로 수행합니다.
