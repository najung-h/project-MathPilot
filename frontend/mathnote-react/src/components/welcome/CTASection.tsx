/**
 * Welcome Page - CTA 섹션
 */

interface CTASectionProps {
  onStartClick: () => void;
}

export function CTASection({ onStartClick }: CTASectionProps) {
  return (
    <section id="start" className="py-52 bg-white hero-pattern">
      <div className="max-w-4xl mx-auto px-8 text-center">
        <h2 className="text-6xl md:text-8xl font-black mb-12 tracking-tighter italic">혁신적인 학습의<br /><span className="gradient-text">첫 프레임</span>을 만드세요.</h2>
        <p className="text-xl md:text-2xl text-slate-500 mb-20 font-medium leading-relaxed italic">"수업 끝나면 책상 위에 놓여 있는 완벽한 복습 노트,<br />지금 바로 경험해보세요."</p>
        <button 
          onClick={onStartClick}
          className="px-20 py-8 bg-indigo-600 text-white text-3xl font-black rounded-[2.5rem] hover:bg-indigo-700 hover:-translate-y-2 transition-all shadow-3xl shadow-indigo-200"
        >
          지금 바로 체험하기
        </button>
        <p className="mt-12 text-slate-400 text-sm font-black uppercase tracking-[0.3em] italic">※ MathPilot 1.0.0 Ready to Launch</p>
      </div>
    </section>
  );
}
