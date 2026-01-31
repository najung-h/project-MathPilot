/**
 * Welcome Page - Header
 */

interface WelcomeHeaderProps {
  onStartClick: () => void;
}

export function WelcomeHeader({ onStartClick }: WelcomeHeaderProps) {
  return (
    <header className="fixed top-0 w-full z-[100] bg-white/90 backdrop-blur-md border-b border-slate-100">
      <div className="max-w-7xl mx-auto px-8 h-20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white font-black text-xl shadow-lg shadow-blue-200">M</div>
          <span className="text-2xl font-black tracking-tighter italic">MathPilot <span className="text-blue-600">AI</span></span>
        </div>
        
        <nav className="hidden lg:flex items-center gap-10 text-sm font-extrabold text-slate-500 uppercase tracking-widest">
          <a href="#overview" className="hover:text-indigo-600 transition">
            Overview
          </a>
          <a href="#tech" className="hover:text-indigo-600 transition">
            Parallel Engine
          </a>
          <a href="#value" className="hover:text-indigo-600 transition">
            Core Value
          </a>
          <a href="#compare" className="hover:text-indigo-600 transition">
            AS-IS vs TO-BE
          </a>
          <button
            onClick={onStartClick}
            className="px-6 py-2.5 bg-indigo-600 text-white rounded-full hover:bg-slate-900 transition shadow-xl shadow-indigo-200"
          >
            Get Started
          </button>
        </nav>
      </div>
    </header>
  );
}
