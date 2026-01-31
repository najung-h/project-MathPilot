/**
 * Welcome Page - Core Value & Compare 섹션
 */

export function OutputSection() {
  return (
    <>
      {/* Core Value Section */}
      <section id="value" className="py-40 bg-slate-50">
        <div className="max-w-7xl mx-auto px-8 text-center mb-24">
          <span className="text-indigo-600 font-black text-sm tracking-[0.3em] uppercase mb-4 block underline underline-offset-8">Core Value</span>
          <h2 className="text-5xl md:text-6xl font-black tracking-tighter italic">듣는 순간, 내 노트가 됩니다.</h2>
        </div>
        <div className="max-w-7xl mx-auto px-8 grid md:grid-cols-3 gap-8">
          <div className="p-12 bg-white rounded-[3.5rem] border border-slate-200 card-hover shadow-sm">
            <div className="w-20 h-20 bg-indigo-600 rounded-3xl flex items-center justify-center text-white text-4xl mb-8 shadow-lg shadow-indigo-100">🔄</div>
            <h4 className="text-2xl font-black mb-4 uppercase tracking-tighter italic">Automated Sync</h4>
            <p className="text-slate-500 font-medium leading-relaxed">슬라이드의 시각 정보와 음성 해설을 AI가 실시간 매핑하여 단권화된 노트를 만듭니다.</p>
          </div>
          <div className="p-12 bg-white rounded-[3.5rem] border border-slate-200 card-hover shadow-sm">
            <div className="w-20 h-20 bg-purple-600 rounded-3xl flex items-center justify-center text-white text-4xl mb-8 shadow-lg shadow-purple-100">🆘</div>
            <h4 className="text-2xl font-black mb-4 uppercase tracking-tighter italic">Interactive Deep-Dive</h4>
            <p className="text-slate-500 font-medium leading-relaxed">이해가 안 가는 구간(SOS)을 표시하면 AI 과외 선생님이 해당 구간의 심층 해설을 제공합니다.</p>
          </div>
          <div className="p-12 bg-white rounded-[3.5rem] border border-slate-200 card-hover shadow-sm">
            <div className="w-20 h-20 bg-pink-600 rounded-3xl flex items-center justify-center text-white text-4xl mb-8 shadow-lg shadow-pink-100">🔍</div>
            <h4 className="text-2xl font-black mb-4 uppercase tracking-tighter italic">Searchable LaTeX</h4>
            <p className="text-slate-500 font-medium leading-relaxed">모든 수식을 LaTeX 기반 마크다운으로 변환합니다. 노션, PDF 어디로든 자유롭게 내보내세요.</p>
          </div>
        </div>
      </section>

      {/* AS-IS vs TO-BE Section */}
      <section id="compare" className="py-40 bg-white">
        <div className="max-w-7xl mx-auto px-8">
          <div className="text-center mb-24">
            <h2 className="text-5xl font-black italic tracking-tighter underline underline-offset-[12px] decoration-indigo-200">"학습의 질이 달라집니다"</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-12 max-w-6xl mx-auto">
            <div className="bg-slate-50 p-12 rounded-[3.5rem] border-2 border-slate-100">
              <div className="flex items-center gap-3 mb-10">
                <span className="text-red-500 font-black text-2xl italic tracking-tighter uppercase">AS-IS</span>
                <div className="h-[2px] flex-1 bg-red-100"></div>
              </div>
              <ul className="space-y-8">
                <li className="flex items-start gap-4 text-slate-400">
                  <span className="text-xl">❌</span>
                  <p className="font-bold text-lg italic">강의자료 따로, 수기 필기 따로</p>
                </li>
                <li className="flex items-start gap-4 text-slate-400">
                  <span className="text-xl">❌</span>
                  <p className="font-bold text-lg italic">모르는 부분 찾으려 영상 10초씩 앞뒤로</p>
                </li>
                <li className="flex items-start gap-4 text-slate-400">
                  <span className="text-xl">❌</span>
                  <p className="font-bold text-lg italic">악필로 다시는 안 보게 되는 복습 노트</p>
                </li>
              </ul>
              <div className="mt-14 p-8 bg-red-50 rounded-3xl border border-red-100 text-red-600 font-black text-center text-xl italic">
                "아... 복잡해 죽겠네 🤯"
              </div>
            </div>
            <div className="bg-indigo-600 p-12 rounded-[3.5rem] shadow-3xl shadow-indigo-200">
              <div className="flex items-center gap-3 mb-10 text-white">
                <span className="font-black text-2xl italic tracking-tighter uppercase">TO-BE</span>
                <div className="h-[2px] flex-1 bg-indigo-400"></div>
              </div>
              <ul className="space-y-8">
                <li className="flex items-start gap-4 text-white">
                  <span className="text-xl">✅</span>
                  <p className="font-bold text-lg italic">AI가 통합한 완벽한 단권화 노트</p>
                </li>
                <li className="flex items-start gap-4 text-white">
                  <span className="text-xl">✅</span>
                  <p className="font-bold text-lg italic">텍스트 검색 한 번에 원하는 구간 이동</p>
                </li>
                <li className="flex items-start gap-4 text-white">
                  <span className="text-xl">✅</span>
                  <p className="font-bold text-lg italic">원클릭 노션 Export로 완성되는 포트폴리오</p>
                </li>
              </ul>
              <div className="mt-14 p-8 bg-white/10 rounded-3xl border border-white/30 text-white font-black text-center text-xl backdrop-blur-lg italic">
                "와... 너무 편하다! ✨"
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
