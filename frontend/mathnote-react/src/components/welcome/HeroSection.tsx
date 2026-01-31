/**
 * Welcome Page - Hero 섹션
 */

interface HeroSectionProps {
  onStartClick: () => void;
}

export function HeroSection({ onStartClick }: HeroSectionProps) {
  return (
    <section className="relative pt-52 pb-32 hero-pattern">
      <div className="max-w-7xl mx-auto px-8 text-center">
        <div className="inline-block px-6 py-2 bg-indigo-50 border border-indigo-100 rounded-full mb-10 shadow-sm">
          <span className="text-sm font-black text-indigo-600 uppercase tracking-[0.2em]">Learning Innovation Solution</span>
        </div>
        <h1 className="text-6xl md:text-8xl font-black leading-tight mb-10 tracking-tighter">
          강의는 <span className="italic text-indigo-600">귀</span>로 듣고,<br />
          필기는 <span className="gradient-text italic text-indigo-600">AI</span>가 끝냅니다.
        </h1>
        <p className="text-xl md:text-2xl text-slate-500 mb-16 max-w-3xl mx-auto leading-relaxed font-medium">
          "필기 강박은 내려놓고, 오직 이해에만 집중하세요.<br />
          기록은 <span className="font-bold text-slate-800">MathPilot</span>이 남깁니다."
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
          <button 
            onClick={onStartClick}
            className="w-full sm:w-auto px-12 py-6 bg-indigo-600 text-white text-xl font-black rounded-2xl hover:bg-indigo-700 hover:-translate-y-2 transition-all shadow-2xl shadow-indigo-200"
          >
            지금 무료로 시작하기
          </button>
          <button className="w-full sm:w-auto px-12 py-6 bg-white border-2 border-slate-200 text-xl font-black rounded-2xl hover:bg-slate-50 transition-all">
            서비스 데모 보기
          </button>
        </div>
      </div>
    </section>
  );
}
