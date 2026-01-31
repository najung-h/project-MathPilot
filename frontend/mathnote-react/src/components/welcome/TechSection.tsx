/**
 * Welcome Page - Tech 섹션
 */

export function TechSection() {
  return (
    <section id="tech" className="py-48 bg-white overflow-hidden">
      <div className="max-w-7xl mx-auto px-8">
        <div className="text-center mb-32">
          <span className="text-indigo-600 font-black text-sm tracking-[0.3em] uppercase mb-4 block underline underline-offset-8">Technology Stack</span>
          <h2 className="text-5xl md:text-7xl font-black tracking-tighter italic">Dual-Track Parallel Engine</h2>
          <p className="mt-8 text-slate-500 font-bold text-lg max-w-2xl mx-auto">시각과 청각 정보를 병렬로 처리하여 <br className="hidden md:block" /> 하나의 완벽한 지식 체계로 통합합니다.</p>
        </div>

        <div className="relative max-w-6xl mx-auto">
          <div className="absolute left-1/2 top-0 bottom-0 w-1 engine-connector hidden lg:block -translate-x-1/2 rounded-full opacity-10"></div>

          <div className="flex flex-col gap-16 lg:gap-24">
            
            <div className="relative grid lg:grid-cols-2 gap-8 lg:gap-32 items-center">
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 hidden lg:flex w-16 h-16 bg-white border-4 border-indigo-600 rounded-full z-20 items-center justify-center font-black text-indigo-600 shadow-xl shadow-indigo-100">01</div>
              
              <div className="bg-slate-50 p-10 rounded-[3rem] border border-slate-100 card-hover text-right relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">📸</div>
                <div className="flex justify-end gap-2 mb-4">
                  <span className="tech-badge bg-indigo-100 text-indigo-600 px-3 py-1 rounded-lg text-xs font-black uppercase">OpenCV</span>
                  <span className="tech-badge bg-slate-200 text-slate-700 px-3 py-1 rounded-lg text-xs font-black uppercase">1 FPS</span>
                </div>
                <h4 className="text-2xl font-black mb-4 italic text-slate-900">프레임 기반 슬라이드 탐지</h4>
                <p className="text-slate-500 font-medium leading-relaxed">화면의 시각적 유사도 변화를 감지하여<br />불필요한 장면은 제거하고 '진짜 슬라이드'만 선별합니다.</p>
              </div>

              <div className="bg-slate-50 p-10 rounded-[3rem] border border-slate-100 card-hover text-left relative overflow-hidden group">
                <div className="absolute top-0 left-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">🎙️</div>
                <div className="flex justify-start gap-2 mb-4">
                  <span className="tech-badge bg-purple-100 text-purple-600 px-3 py-1 rounded-lg text-xs font-black uppercase">Whisper AI</span>
                  <span className="tech-badge bg-slate-200 text-slate-700 px-3 py-1 rounded-lg text-xs font-black uppercase">STT</span>
                </div>
                <h4 className="text-2xl font-black mb-4 italic text-slate-900">고정밀 음성 텍스트화</h4>
                <p className="text-slate-500 font-medium leading-relaxed">강사의 설명을 고정밀 텍스트로 변환하고<br />모든 문장에 정확한 타임스탬프를 부여합니다.</p>
              </div>
            </div>

            <div className="relative grid lg:grid-cols-2 gap-8 lg:gap-32 items-center">
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 hidden lg:flex w-16 h-16 bg-white border-4 border-purple-600 rounded-full z-20 items-center justify-center font-black text-purple-600 shadow-xl shadow-purple-100">02</div>

              <div className="bg-slate-50 p-10 rounded-[3rem] border border-slate-100 card-hover text-right relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">📐</div>
                <div className="flex justify-end gap-2 mb-4">
                  <span className="tech-badge bg-indigo-100 text-indigo-600 px-3 py-1 rounded-lg text-xs font-black uppercase">Vision-Language</span>
                  <span className="tech-badge bg-blue-100 text-blue-600 px-3 py-1 rounded-lg text-xs font-black uppercase">LaTeX</span>
                </div>
                <h4 className="text-2xl font-black mb-4 italic text-slate-900">수학식 구조 디지털화</h4>
                <p className="text-slate-500 font-medium leading-relaxed">이미지 속 복잡한 수식을 파악하여<br />즉시 LaTeX 코드로 변환합니다.</p>
              </div>

              <div className="bg-slate-50 p-10 rounded-[3rem] border border-slate-100 card-hover text-left relative overflow-hidden group">
                <div className="absolute top-0 left-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">🧠</div>
                <div className="flex justify-start gap-2 mb-4">
                  <span className="tech-badge bg-purple-100 text-purple-600 px-3 py-1 rounded-lg text-xs font-black uppercase">GPT-4o</span>
                  <span className="tech-badge bg-pink-100 text-pink-600 px-3 py-1 rounded-lg text-xs font-black uppercase">Context Fusion</span>
                </div>
                <h4 className="text-2xl font-black mb-4 italic text-slate-900">슬라이드 별 문맥 매핑</h4>
                <p className="text-slate-500 font-medium leading-relaxed">Vision 데이터와 오디오를 결합하여<br />각 슬라이드에 최적화된 해설 요약을 자동 생성합니다.</p>
              </div>
            </div>
          </div>

          <div className="mt-32 relative text-center">
            <div className="inline-block p-12 bg-slate-900 rounded-[4rem] text-white shadow-3xl relative z-10 group hover:scale-105 transition-transform border border-slate-800">
              <div className="absolute -top-8 left-1/2 -translate-x-1/2 px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-full text-sm font-black uppercase tracking-[0.2em] shadow-xl">THE MERGE</div>
              <h4 className="text-3xl font-black mb-6 italic tracking-tight">단권화 노트 자동 생성 완료</h4>
              <div className="flex justify-center gap-6">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-xl">📄</div>
                  <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">PDF</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-xl">📝</div>
                  <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">NOTION</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-xl bg-slate-800 flex items-center justify-center text-xl">Ⓜ️</div>
                  <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">MD</span>
                </div>
              </div>
            </div>
            <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-48 bg-indigo-600/30 blur-[120px] -z-0"></div>
          </div>
        </div>
      </div>
    </section>
  );
}
