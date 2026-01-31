/**
 * Main 페이지
 * 강의 분석 및 노트 프리뷰 페이지
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { MainHeader, VideoPlayer, LectureInfo, NotePreview } from '@/components/main';
import { UploadModal } from '@/components/upload';
import { videoService, noteService } from '@/services';
import type { TaskStatusResponse, NoteResponse } from '@/types';
import { ROUTES } from '@/constants';

interface MainPageProps {
  isUploadModalOpen: boolean;
  onCloseUploadModal: () => void;
  onOpenUploadModal: () => void;
}

export function MainPage({
  isUploadModalOpen,
  onCloseUploadModal,
  onOpenUploadModal,
}: MainPageProps) {
  // SOS 타임스탬프 저장
  const [sosTimestamps, setSosTimestamps] = useState<number[]>([]);
  
  // 작업 상태 관리
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatusResponse | null>(null);
  const [noteData, setNoteData] = useState<NoteResponse | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState<string | null>(null);
  const [lectureTitle, setLectureTitle] = useState<string>('강의 영상');
  const navigate = useNavigate();

  // Welcome 페이지로 이동
  const handleLogoClick = () => {
    navigate(ROUTES.WELCOME);
  };

  // 상태 폴링
  const pollTaskStatus = useCallback(async (taskId: string) => {
    try {
      const status = await videoService.getStatus(taskId);
      setTaskStatus(status);
      console.log('Task status:', status);

      // 영상 URL 업데이트 (s3_key가 있으면)
      if (status.s3_key && !videoUrl) {
        const baseUrl = 'http://localhost:8000';
        // s3_key는 "videos/{taskId}/original.mp4" 형식
        setVideoUrl(`${baseUrl}/storage/${status.s3_key}`);
        console.log('Video URL set:', `${baseUrl}/storage/${status.s3_key}`);
      }

      if (status.status === 'completed') {
        // 처리 완료 - 노트 데이터 가져오기
        setIsPolling(false);
        try {
          const note = await noteService.getNote(taskId);
          setNoteData(note);
          console.log('Note data:', note);
        } catch (noteErr) {
          console.error('Failed to fetch note:', noteErr);
        }
      } else if (status.status === 'failed') {
        // 처리 실패
        setIsPolling(false);
        setError(status.error_message || '처리 중 오류가 발생했습니다.');
      }
      // processing, pending, uploaded 상태면 계속 폴링
    } catch (err) {
      console.error('Failed to poll status:', err);
      setError('상태 조회 중 오류가 발생했습니다.');
      setIsPolling(false);
    }
  }, [videoUrl]);

  // 폴링 효과
  useEffect(() => {
    if (!currentTaskId || !isPolling) return;

    const intervalId = setInterval(() => {
      pollTaskStatus(currentTaskId);
    }, 3000); // 3초마다 폴링

    // 초기 폴링
    pollTaskStatus(currentTaskId);

    return () => clearInterval(intervalId);
  }, [currentTaskId, isPolling, pollTaskStatus]);

  const handleSosClick = (timestamp: number) => {
    setSosTimestamps((prev) => [...prev, timestamp]);
    console.log('SOS clicked at:', timestamp, 'Total SOS:', sosTimestamps.length + 1);
  };

  const handleUploadSuccess = (taskId: string, uploadType: 'file' | 'url', fileExtension?: string, youtubeUrlParam?: string) => {
    console.log('Upload success, task ID:', taskId, 'type:', uploadType);
    setCurrentTaskId(taskId);
    setIsPolling(true);
    setError(null);
    setNoteData(null);
    setTaskStatus(null);
    
    // 파일 업로드의 경우 즉시 영상 URL 설정
    if (uploadType === 'file' && fileExtension) {
      const baseUrl = 'http://localhost:8000';
      const videoPath = `${baseUrl}/storage/videos/${taskId}/original.${fileExtension}`;
      setVideoUrl(videoPath);
      setYoutubeUrl(null);
      console.log('Video URL set immediately:', videoPath);
    } else if (uploadType === 'url' && youtubeUrlParam) {
      // YouTube URL의 경우 즉시 iframe으로 표시
      setYoutubeUrl(youtubeUrlParam);
      setVideoUrl(null);
      console.log('YouTube URL set immediately:', youtubeUrlParam);
    } else {
      setVideoUrl(null);
      setYoutubeUrl(null);
    }
  };

  return (
    <div className="bg-slate-50 text-slate-900 min-h-screen font-inter">
      <MainHeader 
        onUploadClick={onOpenUploadModal}
        onLogoClick={handleLogoClick}
      />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* 처리 상태 표시 */}
        {taskStatus && (
          <div className="mb-6 p-4 bg-white rounded-xl shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-slate-700">처리 상태</h3>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                taskStatus.status === 'completed' ? 'bg-green-100 text-green-700' :
                taskStatus.status === 'failed' ? 'bg-red-100 text-red-700' :
                taskStatus.status === 'processing' ? 'bg-blue-100 text-blue-700' :
                'bg-slate-100 text-slate-700'
              }`}>
                {taskStatus.status === 'completed' ? '완료' :
                 taskStatus.status === 'failed' ? '실패' :
                 taskStatus.status === 'processing' ? '처리 중...' :
                 taskStatus.status === 'uploaded' ? '업로드됨' : '대기 중'}
              </span>
            </div>
            
            {taskStatus.progress && taskStatus.status === 'processing' && (
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500 w-16">Vision</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${taskStatus.progress.vision * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-500 w-10">{Math.round(taskStatus.progress.vision * 100)}%</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500 w-16">Audio</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${taskStatus.progress.audio * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-500 w-10">{Math.round(taskStatus.progress.audio * 100)}%</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500 w-16">Synthesis</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-2">
                    <div 
                      className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${taskStatus.progress.synthesis * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-500 w-10">{Math.round(taskStatus.progress.synthesis * 100)}%</span>
                </div>
              </div>
            )}

            {error && (
              <div className="mt-3 p-2 bg-red-50 rounded-lg text-red-600 text-sm">
                {error}
              </div>
            )}
          </div>
        )}

        <div className="grid grid-cols-12 gap-8">
          {/* Left Column - Video & Info */}
          <div className="col-span-12 lg:col-span-7 space-y-6">
            <VideoPlayer 
              videoUrl={videoUrl}
              youtubeUrl={youtubeUrl}
              title={lectureTitle}
              onSosClick={handleSosClick} 
            />
            <LectureInfo 
              taskId={currentTaskId}
              taskStatus={taskStatus}
            />
          </div>

          {/* Right Column - Note Preview */}
          <div className="col-span-12 lg:col-span-5">
            <NotePreview noteData={taskStatus?.status === 'completed' ? noteData : null} />
          </div>
        </div>
      </main>

      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={onCloseUploadModal}
        onUploadSuccess={handleUploadSuccess}
      />
    </div>
  );
}
