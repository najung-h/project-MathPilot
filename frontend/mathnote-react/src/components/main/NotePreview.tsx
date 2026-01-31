/**
 * Main Page - 노트 프리뷰 섹션
 */

import { useEffect, useRef } from 'react';
import katex from 'katex';
import type { SlideData, NoteResponse } from '@/types';

interface NotePreviewProps {
  noteData?: NoteResponse | null;
  isLoading?: boolean;
}

// 기본 데모 슬라이드 데이터
const DEMO_SLIDES: SlideData[] = [
  {
    slide_number: 1,
    timestamp_start: 0,
    timestamp_end: 10.5,
    image_url: '',
    ocr_content: 'A\\mathbf{x} = \\lambda\\mathbf{x}',
    audio_summary: '행렬 A가 벡터 x에 가하는 선형 변환이 단순히 크기만 변화시킬 때, λ를 고유값이라 함.',
    sos_explanation: '여기서 det은 행렬식을 의미하며, 행렬 A - λI가 역행렬을 갖지 않도록 만드는 조건을 찾는 과정입니다.',
  },
];

export function NotePreview({ noteData, isLoading = false }: NotePreviewProps) {
  const equationRef = useRef<HTMLDivElement>(null);
  
  // noteData가 있으면 그것을 사용, 없으면 null
  const slides = noteData?.slides;
  const title = noteData?.title || 'Lecture Summary';

  useEffect(() => {
    if (equationRef.current && slides && slides.length > 0) {
      try {
        katex.render(slides[0].ocr_content, equationRef.current, {
          throwOnError: false,
        });
      } catch (e) {
        console.error('KaTeX render error:', e);
      }
    }
  }, [slides]);

  return (
    <div className="flex flex-col h-[calc(100vh-140px)]">
      {/* Header */}
      <div className="bg-white rounded-t-2xl p-4 border-t border-x border-slate-200 flex justify-between items-center bg-slate-50">
        <span className="text-sm font-bold text-slate-700">
          생성된 단권화 노트 Preview
        </span>
        {noteData && (
          <button className="text-xs bg-white border border-slate-200 px-3 py-1.5 rounded-md shadow-sm hover:shadow-md transition">
            Export to Notion
          </button>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 bg-white border border-slate-200 p-8 overflow-y-auto rounded-b-2xl shadow-inner prose prose-slate max-w-none">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4" />
              <p className="text-slate-500">노트 생성 중...</p>
            </div>
          </div>
        ) : !noteData ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-slate-400">
              <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <p className="text-sm">강의 분석이 완료되면 노트가 표시됩니다</p>
            </div>
          </div>
        ) : (
          <>
            <h1 className="text-2xl font-bold border-b pb-4">
              {title}
            </h1>

            {slides && slides.length > 0 && (
              <>
                <h3 className="mt-6 text-blue-600">1. 핵심 수식 (OCR 추출)</h3>
                <div className="bg-slate-50 p-4 rounded-xl my-4 text-center">
                  <div ref={equationRef} className="text-xl italic" />
                </div>

                <h3 className="mt-6">2. 강의 요약</h3>
                <ul className="list-disc ml-5 space-y-2 text-slate-600 text-sm">
                  <li>
                    {slides[0]?.audio_summary}
                  </li>
                </ul>

                {/* SOS Explanation */}
                {slides[0]?.sos_explanation && (
                  <div className="mt-8 p-5 bg-amber-50 border border-amber-200 rounded-xl relative">
                    <div className="absolute -top-3 left-4 bg-amber-400 text-white text-[10px] font-bold px-2 py-0.5 rounded">
                      💡 AI 심층 해설 (SOS)
                    </div>
                    <p className="text-xs font-semibold text-amber-800 mb-2">
                      "SOS 구간 질문에 대한 해설입니다"
                    </p>
                    <p className="text-sm text-amber-700 leading-relaxed">
                      {slides[0].sos_explanation}
                    </p>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
