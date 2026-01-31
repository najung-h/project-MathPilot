/**
 * Welcome Page - Problem 섹션
 */

export function ProblemSection() {
  return (
    <section id="overview" className="py-40 bg-slate-900 text-white relative overflow-hidden">
      <div className="max-w-7xl mx-auto px-8 relative z-10">
        <div className="grid lg:grid-cols-2 gap-24 items-center">
          <div>
            <h2 className="text-5xl md:text-6xl font-black mb-12 tracking-tight italic">기록하느라 놓쳐버린<br /><span className="text-indigo-400 italic">교수님의 Insight</span></h2>
            <div className="space-y-12">
              <div className="flex gap-6">
                <div className="text-4xl text-indigo-400">01</div>
                <div>
                  <h4 className="text-2xl font-bold mb-2 text-slate-100 uppercase tracking-tighter">멀티태스킹의 한계</h4>
                  <p className="text-slate-400 text-lg leading-relaxed font-medium">복잡한 수식을 옮겨 적다 정작 중요한 개념 설명을 놓친 적이 한두 번이 아닙니다.</p>
                </div>
              </div>
              <div className="flex gap-6">
                <div className="text-4xl text-indigo-400">02</div>
                <div>
                  <h4 className="text-2xl font-bold mb-2 text-slate-100 uppercase tracking-tighter">파편화된 복습 시간</h4>
                  <p className="text-slate-400 text-lg leading-relaxed font-medium">"그 예시가 뭐였지?" 영상을 하염없이 돌려보며 낭비하는 시간이 학습 시간의 40%입니다.</p>
                </div>
              </div>
            </div>
          </div>
          <div className="relative">
            <div className="bg-indigo-600/20 p-12 rounded-[3.5rem] border border-indigo-500/30 backdrop-blur-xl">
              <p className="text-2xl font-medium leading-relaxed italic text-left">
                "전공 수업부터 기술 컨퍼런스까지,<br /> 
                <span className="text-indigo-400 font-black text-3xl underline underline-offset-8">수식과 도표</span>가 많은 모든 곳에<br /> 
                필요한 유일한 솔루션입니다."
              </p>
              <div className="mt-8 flex gap-4 justify-start">
                <span className="px-5 py-2.5 bg-slate-800 rounded-full text-xs font-black text-indigo-300">#공대생</span>
                <span className="px-5 py-2.5 bg-slate-800 rounded-full text-xs font-black text-indigo-300">#개발자</span>
                <span className="px-5 py-2.5 bg-slate-800 rounded-full text-xs font-black text-indigo-300">#수학전공</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
