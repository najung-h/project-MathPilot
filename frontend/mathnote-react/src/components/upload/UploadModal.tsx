/**
 * Upload Modal 컴포넌트
 */

import { useState, useRef, type ChangeEvent, type DragEvent } from 'react';
import { Modal, Button } from '@/components/common';
import { APP_CONFIG } from '@/constants';
import { videoService } from '@/services';

type UploadMode = 'file' | 'url';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess?: (taskId: string, uploadType: 'file' | 'url', fileExtension?: string, youtubeUrl?: string) => void;
}

export function UploadModal({ isOpen, onClose, onUploadSuccess }: UploadModalProps) {
  const [mode, setMode] = useState<UploadMode>('file');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [frameInterval, setFrameInterval] = useState(1);
  const [latexMode, setLatexMode] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const validateAndSetFile = (file: File) => {
    setError(null);
    
    // 파일 타입 검증
    if (!(APP_CONFIG.UPLOAD.ALLOWED_FILE_TYPES as readonly string[]).includes(file.type)) {
      setError('지원하지 않는 파일 형식입니다. MP4 또는 MOV 파일만 업로드 가능합니다.');
      return;
    }
    
    // 파일 크기 검증
    const maxSizeBytes = APP_CONFIG.UPLOAD.MAX_FILE_SIZE_MB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      setError(`파일 크기가 너무 큽니다. 최대 ${APP_CONFIG.UPLOAD.MAX_FILE_SIZE_MB}MB까지 업로드 가능합니다.`);
      return;
    }
    
    setSelectedFile(file);
  };

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const file = e.dataTransfer.files?.[0];
    if (file) {
      validateAndSetFile(file);
    }
  };

  const handleSubmit = async () => {
    setError(null);
    setIsUploading(true);

    try {
      if (mode === 'file' && selectedFile) {
        // 파일 업로드
        const uploadResponse = await videoService.uploadFile(selectedFile);
        
        // 파일 확장자 추출
        const extension = selectedFile.name.split('.').pop() || 'mp4';
        
        // 처리 시작
        await videoService.processVideo(uploadResponse.task_id, {
          options: {
            frame_interval_sec: frameInterval,
            ssim_threshold: APP_CONFIG.DEFAULT_PROCESS_OPTIONS.ssim_threshold,
          },
        });
        
        onUploadSuccess?.(uploadResponse.task_id, 'file', extension);
      } else if (mode === 'url' && youtubeUrl) {
        // URL 유효성 검사
        const trimmedUrl = youtubeUrl.trim();
        if (!trimmedUrl.startsWith('http://') && !trimmedUrl.startsWith('https://')) {
          setError('올바른 URL 형식이 아닙니다. http:// 또는 https://로 시작해야 합니다.');
          setIsUploading(false);
          return;
        }

        // URL에서 영상 가져오기
        const response = await videoService.fetchFromUrl({
          url: trimmedUrl,
          sos_timestamps: [],
        });
        
        onUploadSuccess?.(response.task_id, 'url', undefined, trimmedUrl);
      }
      
      // 모달 닫기 및 상태 초기화
      handleClose();
    } catch (err: any) {
      console.error('Upload error:', err);
      // 에러 메시지를 깔끔하게 추출
      const errorMessage = err?.response?.data?.detail || 
                          err?.message || 
                          '업로드 중 오류가 발생했습니다. 다시 시도해주세요.';
      setError(errorMessage);
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setYoutubeUrl('');
    setError(null);
    setIsUploading(false);
    onClose();
  };

  const isSubmitDisabled = 
    isUploading || 
    (mode === 'file' && !selectedFile) || 
    (mode === 'url' && !youtubeUrl.trim());

  return (
    <Modal isOpen={isOpen} onClose={handleClose}>
      <div className="p-8">
        {/* Close Button */}
        <button
          onClick={handleClose}
          className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 transition"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>

        {/* Header */}
        <h3 className="text-2xl font-bold mb-2">강의 분석 시작하기</h3>
        <p className="text-slate-500 text-sm mb-8">
          영상을 업로드하면 AI가 슬라이드와 음성을 분석합니다.
        </p>

        {/* Mode Tabs */}
        <div className="flex gap-2 p-1 bg-slate-100 rounded-xl mb-6">
          <button
            onClick={() => setMode('file')}
            className={`flex-1 py-2 text-sm font-bold rounded-lg transition ${
              mode === 'file'
                ? 'bg-white shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            파일 업로드
          </button>
          <button
            onClick={() => setMode('url')}
            className={`flex-1 py-2 text-sm font-bold rounded-lg transition ${
              mode === 'url'
                ? 'bg-white shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            YouTube 링크
          </button>
        </div>

        {/* Upload Area */}
        {mode === 'file' ? (
          <div
            onClick={() => fileInputRef.current?.click()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition group ${
              isDragOver
                ? 'border-blue-500 bg-blue-50'
                : selectedFile
                ? 'border-green-500 bg-green-50'
                : 'border-slate-200 hover:border-blue-500 hover:bg-blue-50/50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={APP_CONFIG.UPLOAD.ALLOWED_EXTENSIONS.join(',')}
              onChange={handleFileSelect}
              className="hidden"
            />
            <div
              className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 transition ${
                selectedFile ? 'bg-green-100' : 'bg-blue-50 group-hover:scale-110'
              }`}
            >
              {selectedFile ? (
                <svg
                  className="w-8 h-8 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-8 h-8 text-blue-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              )}
            </div>
            <p className="font-bold text-slate-700">
              {selectedFile ? selectedFile.name : '강의 영상 드래그 또는 클릭'}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              {selectedFile
                ? `${(selectedFile.size / (1024 * 1024)).toFixed(1)}MB`
                : `MP4, MOV (최대 ${APP_CONFIG.UPLOAD.MAX_FILE_SIZE_MB}MB)`}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <input
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              className="w-full px-4 py-4 border-2 border-slate-200 rounded-xl text-sm focus:border-blue-500 focus:outline-none transition"
            />
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-600 text-sm">
            {error}
          </div>
        )}

        {/* Options */}
        <div className="mt-8 space-y-4">
          <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100">
            <div>
              <p className="text-sm font-bold text-slate-700">추출 정밀도</p>
              <p className="text-[11px] text-slate-400 font-medium">
                슬라이드 전환 탐지 주기를 설정합니다.
              </p>
            </div>
            <select
              value={frameInterval}
              onChange={(e) => setFrameInterval(Number(e.target.value))}
              className="bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-xs font-bold outline-none focus:ring-2 focus:ring-blue-500"
            >
              {APP_CONFIG.FRAME_INTERVAL_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-3 px-1">
            <input
              type="checkbox"
              id="latexMode"
              checked={latexMode}
              onChange={(e) => setLatexMode(e.target.checked)}
              className="w-4 h-4 rounded text-blue-600 border-slate-300 focus:ring-blue-500"
            />
            <label htmlFor="latexMode" className="text-xs font-bold text-slate-600">
              LaTeX 수식 정밀 변환 모드 활성화
            </label>
          </div>
        </div>

        {/* Submit Button */}
        <Button
          variant="primary"
          size="lg"
          fullWidth
          onClick={handleSubmit}
          disabled={isSubmitDisabled}
          className={`mt-8 flex items-center justify-center gap-2 ${
            isSubmitDisabled ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isUploading ? (
            <>
              <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full" />
              <span>업로드 중...</span>
            </>
          ) : (
            <>
              <span>분석 및 노트 생성 시작</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            </>
          )}
        </Button>
      </div>
    </Modal>
  );
}
