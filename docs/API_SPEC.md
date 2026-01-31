# MathNote API Specification (v1)

**Base URL:** `http://localhost:8000`
**API Prefix:** `/api/v1`

---

## 1. Common

### GET `/health`
서버 상태 확인
- **Response (`HealthResponse`):**
  ```json
  {
    "status": "healthy"
  }
  ```

---

## 2. Static Assets (정적 파일)
- **Base URL:** `http://localhost:8000/static`
- **설명:** 업로드된 영상, 추출된 프레임, 생성된 노트 등이 서빙되는 경로입니다. (로컬 스토리지 사용 시)

---

## 3. Video API (`/api/v1/videos`)

### POST `/fetch-url`
외부 URL(YouTube 등)에서 영상을 다운로드하고 처리를 시작합니다.
- **Request Body (`VideoUrlRequest`):**
  ```json
  {
    "url": "https://www.youtube.com/watch?v=...",
    "sos_timestamps": []
  }
  ```
  - `url` (string, required): 비디오 URL (YouTube 등)
  - `sos_timestamps` (array[float], optional): SOS 요청 타임스탬프 목록 (초 단위), 기본값은 빈 배열

- **Response (`ProcessVideoResponse`):**
  ```json
  {
    "task_id": "5bb4c5b6-df5b-4945-906e-31c4a7955a9f",
    "status": "processing",
    "estimated_time_sec": 300
  }
  ```
  - `task_id` (string): 작업 ID (UUID)
  - `status` (string): 항상 "processing"
  - `estimated_time_sec` (integer): 예상 처리 시간 (초)

### POST `/upload`
로컬 영상 파일을 서버로 업로드합니다.
- **Request Body:** Multipart/form-data
  - `file` (UploadFile, required): 비디오 파일

- **Response (`UploadResponse`):**
  ```json
  {
    "task_id": "uuid-string",
    "file_url": "http://localhost:8000/static/videos/uuid/original.mp4",
    "status": "uploaded"
  }
  ```
  - `task_id` (string): 작업 ID (UUID)
  - `file_url` (string): 파일 URL (정적 경로)
  - `status` (string): 항상 "uploaded"

### POST `/{task_id}/process`
업로드된 영상에 대해 수동으로 처리 파이프라인을 시작합니다.
- **Path Parameters:**
  - `task_id` (string, required): 작업 ID

- **Request Body (`ProcessVideoRequest`):**
  ```json
  {
    "sos_timestamps": [123.5, 456.2],
    "options": {
      "frame_interval_sec": 1.0,
      "ssim_threshold": 0.85
    }
  }
  ```
  - `sos_timestamps` (array[float], optional): SOS 요청 타임스탬프 목록 (초), 기본값은 빈 배열
  - `options` (object, optional): 처리 옵션 (미지정 시 기본값 사용)
    - `frame_interval_sec` (float, optional): 프레임 추출 간격 (초), 범위: 0.1~10.0
    - `ssim_threshold` (float, optional): 슬라이드 전환 감지 임계값, 범위: 0.5~1.0

- **Response (`ProcessVideoResponse`):**
  ```json
  {
    "task_id": "uuid-string",
    "status": "processing",
    "estimated_time_sec": 120
  }
  ```

### GET `/{task_id}/status`
작업의 현재 상태와 진행률을 조회합니다.
- **Path Parameters:**
  - `task_id` (string, required): 작업 ID

- **Response (`TaskStatusResponse`):**
  ```json
  {
    "task_id": "uuid-string",
    "status": "processing",
    "progress": {
      "vision": 0.5,
      "audio": 0.5,
      "synthesis": 0.0
    },
    "error_message": null
  }
  ```
  - `task_id` (string): 작업 ID
  - `status` (string): 작업 상태 - `pending`, `uploaded`, `processing`, `completed`, `failed` 중 하나
  - `progress` (object): 진행률 상세
    - `vision` (float): Vision 처리 진행률 (0.0~1.0)
    - `audio` (float): Audio 처리 진행률 (0.0~1.0)
    - `synthesis` (float): Synthesis 진행률 (0.0~1.0)
  - `error_message` (string | null): 에러 메시지 (실패 시에만)

---

## 4. Note API (`/api/v1/notes`)

### GET `/{task_id}`
완료된 노트의 구조화된 데이터를 조회합니다.
- **Path Parameters:**
  - `task_id` (string, required): 작업 ID

- **Response (`NoteResponse`):**
  ```json
  {
    "task_id": "uuid-string",
    "title": "Untitled Note",
    "created_at": "2026-01-31T12:00:00Z",
    "slides": [
      {
        "slide_number": 1,
        "timestamp_start": 0.0,
        "timestamp_end": 10.5,
        "image_url": "http://localhost:8000/static/processing/uuid/slides/slide_001.jpg",
        "ocr_content": "# 제목\n수식: $E=mc^2$",
        "audio_summary": "이 구간에서는 에너지와 질량의 등가성에 대해 설명합니다.",
        "sos_explanation": null
      }
    ]
  }
  ```
  - `task_id` (string): 작업 ID
  - `title` (string): 노트 제목
  - `created_at` (string): 생성 시간 (ISO 8601 형식)
  - `slides` (array): 슬라이드 목록
    - `slide_number` (integer): 슬라이드 번호
    - `timestamp_start` (float): 시작 타임스탬프 (초)
    - `timestamp_end` (float): 종료 타임스탬프 (초)
    - `image_url` (string): 슬라이드 이미지 URL (Presigned URL 또는 정적 경로)
    - `ocr_content` (string): OCR 결과 (LaTeX 포함 마크다운)
    - `audio_summary` (string): 해당 구간 음성 요약
    - `sos_explanation` (string | null): SOS 심층 해설 (SOS 타임스탬프가 있을 때만)

- **Error:** 작업이 완료되지 않았거나 존재하지 않는 경우 404 반환

### GET `/{task_id}/download`
마크다운 파일 다운로드 링크를 생성합니다.
- **Path Parameters:**
  - `task_id` (string, required): 작업 ID

- **Response (`NoteDownloadResponse`):**
  ```json
  {
    "download_url": "http://localhost:8000/static/outputs/uuid/note.md",
    "filename": "note_uuid.md",
    "expires_at": "2026-01-31T13:00:00Z"
  }
  ```
  - `download_url` (string): 다운로드 URL (Presigned URL 또는 정적 경로)
  - `filename` (string): 파일명
  - `expires_at` (string): URL 만료 시간 (ISO 8601 형식)

- **Error:** 작업이 완료되지 않았거나 존재하지 않는 경우 404 반환

### GET `/{task_id}/slides/{slide_number}/image`
특정 슬라이드 이미지의 개별 접근 URL을 조회합니다.
- **Path Parameters:**
  - `task_id` (string, required): 작업 ID
  - `slide_number` (integer, required): 슬라이드 번호

- **Response (`SlideImageResponse`):**
  ```json
  {
    "image_url": "http://localhost:8000/static/processing/uuid/slides/slide_001.jpg",
    "expires_at": "2026-01-31T13:00:00Z"
  }
  ```
  - `image_url` (string): 이미지 URL (Presigned URL 또는 정적 경로)
  - `expires_at` (string): URL 만료 시간 (ISO 8601 형식)

- **Error:** 작업이 존재하지 않는 경우 404 반환

---

## 5. Error Responses

모든 API는 에러 발생 시 다음 형식으로 응답합니다:

```json
{
  "detail": "에러 상세 메시지"
}
```

**일반적인 HTTP 상태 코드:**
- `200 OK`: 요청 성공
- `400 Bad Request`: 잘못된 요청 (파라미터 유효성 검사 실패 등)
- `404 Not Found`: 리소스를 찾을 수 없음 (존재하지 않는 task_id 등)
- `422 Unprocessable Entity`: 요청 본문의 스키마 검증 실패
- `500 Internal Server Error`: 서버 내부 오류
