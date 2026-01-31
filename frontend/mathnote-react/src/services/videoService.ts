/**
 * Video API 서비스
 */

import { apiClient } from './apiClient';
import { API_ENDPOINTS } from '@/constants';
import type {
  VideoUrlRequest,
  UploadResponse,
  ProcessVideoRequest,
  ProcessVideoResponse,
  TaskStatusResponse,
} from '@/types';

export const videoService = {
  /**
   * YouTube 등 외부 URL에서 영상 다운로드 및 처리 시작
   */
  fetchFromUrl: async (data: VideoUrlRequest): Promise<ProcessVideoResponse> => {
    const response = await apiClient.post<ProcessVideoResponse>(
      API_ENDPOINTS.VIDEO.FETCH_URL,
      data
    );
    return response.data;
  },

  /**
   * 로컬 파일 업로드
   */
  uploadFile: async (file: File): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<UploadResponse>(
      API_ENDPOINTS.VIDEO.UPLOAD,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * 업로드된 영상 처리 시작
   */
  processVideo: async (
    taskId: string,
    data: ProcessVideoRequest
  ): Promise<ProcessVideoResponse> => {
    const response = await apiClient.post<ProcessVideoResponse>(
      API_ENDPOINTS.VIDEO.PROCESS(taskId),
      data
    );
    return response.data;
  },

  /**
   * 강의 요약 생성 시작
   */
  generateSummary: async (taskId: string): Promise<ProcessVideoResponse> => {
    const response = await apiClient.post<ProcessVideoResponse>(
      `/api/v1/videos/${taskId}/generate-summary`
    );
    return response.data;
  },

  /**
   * SOS 타임스탬프 추가
   */
  addSosTimestamp: async (taskId: string, timestamp: number): Promise<void> => {
    await apiClient.post(
      `/api/v1/videos/${taskId}/sos`,
      { timestamp }
    );
  },

  /**
   * 작업 상태 조회
   */
  getStatus: async (taskId: string): Promise<TaskStatusResponse> => {
    const response = await apiClient.get<TaskStatusResponse>(
      API_ENDPOINTS.VIDEO.STATUS(taskId)
    );
    return response.data;
  },
};
