/**
 * Main Page - 강의 정보 섹션
 */

import { useState } from 'react';
import type { TaskStatusResponse } from '@/types';
import { videoService } from '@/services';

interface LectureInfoProps {
  taskId?: string | null;
  taskStatus?: TaskStatusResponse | null;
  onStartPolling?: () => void;
}

export function LectureInfo({ taskId, taskStatus, onStartPolling }: LectureInfoProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateSummary = async () => {
    if (!taskId) return;
    
    setIsGenerating(true);
    try {
      await videoService.generateSummary(taskId);
      console.log('Summary generation started');
      // 폴링 재시작
      onStartPolling?.();
    } catch (err) {
      console.error('Failed to generate summary:', err);
      alert('강의 요약 생성에 실패했습니다.');
    } finally {
      setIsGenerating(false);
    }
  };

  if (!taskId || !taskStatus) {
    return (
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <span className="w-2 h-6 bg-blue-600 rounded-full" />
          강의 정보
        </h2>
        
        <p className="mt-4 text-slate-500 text-sm leading-relaxed text-center py-8">
          강의 영상을 업로드하면 정보가 표시됩니다
        </p>
      </div>
    );
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '분석 완료';
      case 'generating_summary': return '요약 생성 중...';
      case 'ready_for_synthesis': return '요약 준비 완료';
      case 'processing': return '분석 중...';
      case 'failed': return '분석 실패';
      case 'uploaded': return '업로드 완료';
      case 'pending': return '대기 중';
      default: return status;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-50 text-green-600 border-green-100';
      case 'generating_summary': return 'bg-purple-50 text-purple-600 border-purple-100';
      case 'ready_for_synthesis': return 'bg-yellow-50 text-yellow-600 border-yellow-100';
      case 'processing': return 'bg-blue-50 text-blue-600 border-blue-100';
      case 'failed': return 'bg-red-50 text-red-600 border-red-100';
      default: return 'bg-slate-50 text-slate-600 border-slate-100';
    }
  };

  // audio와 vision이 모두 완료되었는지 확인
  const isReadyForSummary = taskStatus.status === 'ready_for_synthesis';
  const isSummaryGenerating = taskStatus.status === 'generating_summary';
  const isCompleted = taskStatus.status === 'completed';
  const showSummaryButton = isReadyForSummary || isSummaryGenerating || isCompleted;

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
      <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
        <span className="w-2 h-6 bg-blue-600 rounded-full" />
        강의 정보
      </h2>
      
      <div className="space-y-3">
        {taskStatus.filename && (
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold text-slate-500 w-20">강의명</span>
            <span className="text-sm text-slate-700 truncate flex-1">{taskStatus.filename}</span>
          </div>
        )}
        
        {taskStatus.channel_name && (
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold text-slate-500 w-20">채널</span>
            <span className="text-sm text-slate-600 truncate flex-1">{taskStatus.channel_name}</span>
          </div>
        )}
        
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-slate-500 w-20">상태</span>
          <span className={`px-3 py-1 text-xs font-semibold rounded-md border ${getStatusColor(taskStatus.status)}`}>
            {getStatusText(taskStatus.status)}
          </span>
        </div>

        {/* 강의요약 생성 버튼 */}
        {showSummaryButton && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <button
              onClick={handleGenerateSummary}
              disabled={isGenerating || isSummaryGenerating}
              className={
                `w-full px-4 py-3 rounded-lg font-semibold text-sm transition-all ${
                  isGenerating || isSummaryGenerating
                    ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                    : isCompleted
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white hover:shadow-lg hover:scale-[1.02] active:scale-95'
                    : 'bg-gradient-to-r from-blue-500 to-purple-500 text-white hover:shadow-lg hover:scale-[1.02] active:scale-95'
                }`
              }
            >
              {isSummaryGenerating ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  요약 생성 중...
                </span>
              ) : isCompleted ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  요약 다시 생성하기
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  강의 요약 생성하기
                </span>
              )}
            </button>
          </div>
        )}

        {taskStatus.status === 'processing' && taskStatus.progress && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <span className="text-sm font-semibold text-slate-500 mb-2 block">진행률</span>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-600">영상 분석</span>
                <span className="font-semibold text-blue-600">{Math.round(taskStatus.progress.vision * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">음성 분석</span>
                <span className="font-semibold text-green-600">{Math.round(taskStatus.progress.audio * 100)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">노트 생성</span>
                <span className="font-semibold text-purple-600">{Math.round(taskStatus.progress.synthesis * 100)}%</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
