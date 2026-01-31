/**
 * API 요청/응답 타입 정의
 * API_SPEC.md 기반
 */

// ============ Video API Types ============

// POST /videos/fetch-url Request
export interface VideoUrlRequest {
  url: string;
  sos_timestamps?: number[];
}

// POST /videos/upload Response
export interface UploadResponse {
  task_id: string;
  file_url: string;
  status: 'uploaded';
}

// POST /videos/{task_id}/process Request
export interface ProcessVideoRequest {
  sos_timestamps?: number[];
  options?: ProcessOptions;
}

export interface ProcessOptions {
  frame_interval_sec?: number;
  ssim_threshold?: number;
}

// POST /videos/fetch-url, /videos/{task_id}/process Response
export interface ProcessVideoResponse {
  task_id: string;
  status: 'processing';
  estimated_time_sec?: number;
}

// GET /videos/{task_id}/status Response
export interface TaskStatusResponse {
  task_id: string;
  status: 'pending' | 'uploaded' | 'processing' | 'ready_for_synthesis' | 'generating_summary' | 'completed' | 'failed';
  progress?: TaskProgress;
  error_message?: string | null;
  filename?: string;
  s3_key?: string;
  channel_name?: string;
}

export interface TaskProgress {
  vision: number;
  audio: number;
  synthesis: number;
}

// ============ Note API Types ============

// GET /notes/{task_id} Response
export interface NoteResponse {
  task_id: string;
  title: string;
  created_at: string;
  slides: SlideData[];
}

export interface SlideData {
  slide_number: number;
  timestamp_start: number;
  timestamp_end: number;
  image_url: string;
  ocr_content: string;
  audio_summary: string;
  sos_explanation?: string;
}

// GET /notes/{task_id}/download Response
export interface NoteDownloadResponse {
  download_url: string;
  filename: string;
  expires_at: string;
}

// ============ Common Types ============

export interface HealthResponse {
  status: 'healthy';
}

// API Error Response
export interface ApiError {
  detail: string;
  status_code?: number;
}
