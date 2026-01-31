/**
 * Main Page - 강의 정보 섹션
 */

import type { TaskStatusResponse } from '@/types';

interface LectureInfoProps {
  taskId?: string | null;
  taskStatus?: TaskStatusResponse | null;
}

export function LectureInfo({ taskId, taskStatus }: LectureInfoProps) {
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
      case 'processing': return 'bg-blue-50 text-blue-600 border-blue-100';
      case 'failed': return 'bg-red-50 text-red-600 border-red-100';
      default: return 'bg-slate-50 text-slate-600 border-slate-100';
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
      <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
        <span className="w-2 h-6 bg-blue-600 rounded-full" />
        강의 정보
      </h2>
      
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-slate-500 w-20">작업 ID</span>
          <span className="text-sm text-slate-700 font-mono">{taskId.slice(0, 8)}...</span>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-slate-500 w-20">상태</span>
          <span className={`px-3 py-1 text-xs font-semibold rounded-md border ${getStatusColor(taskStatus.status)}`}>
            {getStatusText(taskStatus.status)}
          </span>
        </div>

        {taskStatus.filename && (
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold text-slate-500 w-20">파일명</span>
            <span className="text-sm text-slate-700 truncate">{taskStatus.filename}</span>
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
