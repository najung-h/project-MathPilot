/**
 * Welcome Page - Footer
 */

export function WelcomeFooter() {
  return (
    <footer className="py-20 border-t border-slate-100 bg-slate-50">
      <div className="max-w-7xl mx-auto px-8 flex flex-col md:flex-row justify-between items-center gap-10">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-black text-sm">M</div>
          <span className="text-2xl font-black tracking-tighter italic text-blue-600">MathPilot AI</span>
        </div>
        <p className="text-slate-400 font-bold text-sm tracking-tight italic">© 2026 MathPilot. All-in-One Learning Innovation.</p>
        <div className="flex gap-10 text-xs font-black text-slate-400 uppercase tracking-[0.2em]">
          <a href="#" className="hover:text-indigo-600 transition">GitHub</a>
          <a href="#" className="hover:text-indigo-600 transition">Contact</a>
          <a href="#" className="hover:text-indigo-600 transition">Privacy</a>
        </div>
      </div>
    </footer>
  );
}
