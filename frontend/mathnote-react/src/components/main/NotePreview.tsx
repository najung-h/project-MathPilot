/**
 * Main Page - 노트 프리뷰 섹션
 */

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import type { NoteResponse } from '@/types';

interface NotePreviewProps {
  noteData?: NoteResponse | null;
  isLoading?: boolean;
  filename?: string | null;
}

export function NotePreview({ noteData, isLoading = false, filename }: NotePreviewProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'original'>('preview');
  
  // noteData가 있으면 그것을 사용, 없으면 null
  const slides = noteData?.slides;
  
  // 제목 우선순위: 1. filename (영상명) 2. noteData.title 3. 기본값
  const title = filename || noteData?.title || 'Lecture Summary';

  return (
    <div className="flex flex-col h-[calc(100vh-140px)]">
      {/* Header with Tabs */}
      <div className="bg-white rounded-t-2xl border-t border-x border-slate-200 bg-slate-50">
        <div className="flex items-center justify-between p-4 border-b border-slate-200">
          <div className="flex gap-2">
            <button
              onClick={() => setActiveTab('preview')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                activeTab === 'preview'
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:bg-slate-100'
              }`}
            >
              📝 생성된 단권화 노트
            </button>
            <button
              onClick={() => setActiveTab('original')}
              className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                activeTab === 'original'
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:bg-slate-100'
              }`}
            >
              🎬 원본 자료
            </button>
          </div>
          {noteData && (
            <button className="text-xs bg-white border border-slate-200 px-3 py-1.5 rounded-md shadow-sm hover:shadow-md transition">
              Export to Notion
            </button>
          )}
        </div>
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
        ) : activeTab === 'preview' ? (
          // 생성된 단권화 노트
          <>
            <h1 className="text-2xl font-bold border-b pb-4">
              {title}
            </h1>

            {slides && slides.length > 0 && slides.map((slide, index) => (
              <div key={slide.slide_number} className="mb-8">
                <h2 className="text-xl font-bold text-slate-800 mt-8 mb-4 flex items-center gap-2">
                  <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">
                    슬라이드 {slide.slide_number}
                  </span>
                  <span className="text-sm text-slate-500 font-normal">
                    {Math.floor(slide.timestamp_start / 60)}:{String(Math.floor(slide.timestamp_start % 60)).padStart(2, '0')} - {Math.floor(slide.timestamp_end / 60)}:{String(Math.floor(slide.timestamp_end % 60)).padStart(2, '0')}
                  </span>
                </h2>

                <h3 className="mt-6 text-blue-600 font-semibold">📊 핵심 수식 (OCR 추출)</h3>
                <div className="bg-slate-50 p-4 rounded-xl my-4 text-left text-xs leading-relaxed">
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {slide.ocr_content}
                  </ReactMarkdown>
                </div>

                <h3 className="mt-6 text-green-600 font-semibold">📝 강의 요약</h3>
                <div className="text-slate-700 text-sm leading-relaxed bg-green-50 p-4 rounded-xl my-4">
                  <ReactMarkdown
                    remarkPlugins={[remarkMath]}
                    rehypePlugins={[rehypeKatex]}
                  >
                    {slide.audio_summary}
                  </ReactMarkdown>
                </div>

                {/* SOS Explanation */}
                {slide.sos_explanation && (
                  <div className="mt-6 p-5 bg-amber-50 border border-amber-200 rounded-xl relative">
                    <div className="absolute -top-3 left-4 bg-amber-400 text-white text-[10px] font-bold px-2 py-0.5 rounded">
                      💡 AI 심층 해설 (SOS)
                    </div>
                    <p className="text-xs font-semibold text-amber-800 mb-2">
                      "이해하기 어려웠던 부분에 대한 상세 해설입니다"
                    </p>
                    <div className="text-sm text-amber-700 leading-relaxed">
                      <ReactMarkdown
                        remarkPlugins={[remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                      >
                        {slide.sos_explanation}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}

                {/* 슬라이드 구분선 */}
                {index < slides.length - 1 && (
                  <hr className="my-8 border-slate-200" />
                )}
              </div>
            ))}
          </>
        ) : (
          // 원본 자료 (Original Output)
          <>
            <h1 className="text-2xl font-bold border-b pb-4">
              {title} - 원본 자료
            </h1>

            {slides && slides.length > 0 && slides.map((slide, index) => (
              <div key={`original-${slide.slide_number}`} className="mb-8">
                <h2 className="text-xl font-bold text-slate-800 mt-8 mb-4 flex items-center gap-2">
                  <span className="bg-purple-500 text-white px-3 py-1 rounded-full text-sm">
                    슬라이드 {slide.slide_number}
                  </span>
                  <span className="text-sm text-slate-500 font-normal">
                    {Math.floor(slide.timestamp_start / 60)}:{String(Math.floor(slide.timestamp_start % 60)).padStart(2, '0')} - {Math.floor(slide.timestamp_end / 60)}:{String(Math.floor(slide.timestamp_end % 60)).padStart(2, '0')}
                  </span>
                </h2>

                {/* 슬라이드 이미지 */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-slate-600 mb-2">📸 슬라이드 이미지</h3>
                  <div className="border border-slate-200 rounded-lg overflow-hidden bg-slate-50">
                    <img 
                      src={slide.image_url} 
                      alt={`Slide ${slide.slide_number}`}
                      className="w-full h-auto"
                      onError={(e) => {
                        e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="800" height="600" fill="%23f1f5f9"/><text x="50%" y="50%" font-size="20" fill="%2364748b" text-anchor="middle" dominant-baseline="middle">이미지를 불러올 수 없습니다</text></svg>';
                      }}
                    />
                  </div>
                </div>

                {/* STT 원본 텍스트 */}
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-slate-600 mb-2">🎤 음성 전사 원본 (STT)</h3>
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
                      {slide.raw_transcript || '음성 전사 데이터가 없습니다.'}
                    </p>
                  </div>
                </div>

                {/* 슬라이드 구분선 */}
                {index < slides.length - 1 && (
                  <hr className="my-8 border-slate-300" />
                )}
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
