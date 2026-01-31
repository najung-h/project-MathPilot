/**
 * Main Page - 네비게이션 헤더
 */

import { Logo, Button } from '@/components/common';

interface MainHeaderProps {
  onUploadClick: () => void;
  onLogoClick?: () => void;
}

export function MainHeader({ onUploadClick, onLogoClick }: MainHeaderProps) {
  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 glass-morphism">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div 
          onClick={onLogoClick}
          className="cursor-pointer transition-opacity hover:opacity-80"
          title="Welcome 페이지로 돌아가기"
        >
          <Logo size="md" />
        </div>
        
        <div className="flex items-center gap-4">
          <Button variant="ghost" className="rounded-full">
            강의 목록
          </Button>
          <Button
            variant="primary"
            onClick={onUploadClick}
            className="rounded-full shadow-md"
          >
            새 강의 업로드
          </Button>
        </div>
      </div>
    </nav>
  );
}
