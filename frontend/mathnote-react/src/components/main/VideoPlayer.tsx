/**
 * Main Page - 비디오 플레이어 섹션
 */

import { useRef, useState, useEffect } from 'react';

interface VideoPlayerProps {
  title?: string;
  videoUrl?: string | null;
  onSosClick?: (timestamp: number) => void;
}

export function VideoPlayer({ 
  title = '강의 영상',
  videoUrl,
  onSosClick 
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const handleSosClick = () => {
    const currentTimestamp = videoRef.current?.currentTime || 0;
    onSosClick?.(currentTimestamp);
  };

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (!document.fullscreenElement) {
        videoRef.current.requestFullscreen();
        setIsFullscreen(true);
      } else {
        document.exitFullscreen();
        setIsFullscreen(false);
      }
    }
  };

  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
    };
  }, []);

  return (
    <div className="relative aspect-video bg-black rounded-2xl overflow-hidden shadow-2xl border-4 border-white">
      {videoUrl ? (
        <>
          <video
            ref={videoRef}
            className="w-full h-full object-contain"
            src={videoUrl}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            controls
          />
          
          {/* Control Overlay */}
          <div className="absolute bottom-6 left-6 right-6 flex items-center justify-between">
            {/* SOS Button */}
            <button
              onClick={handleSosClick}
              className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-full font-bold shadow-lg flex items-center gap-2 transform active:scale-95 transition z-10"
            >
              <span className="text-xl">🤯</span>
              <span>잘 모르겠어요! (SOS)</span>
            </button>

            {/* Fullscreen Button */}
            <button
              onClick={handleFullscreen}
              className="bg-slate-800/80 hover:bg-slate-700 text-white px-4 py-3 rounded-full shadow-lg transform active:scale-95 transition z-10"
              title={isFullscreen ? '전체화면 종료' : '전체화면'}
            >
              {isFullscreen ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 9V4.5M9 9H4.5M9 9L3.75 3.75M9 15v4.5M9 15H4.5M9 15l-5.25 5.25M15 9h4.5M15 9V4.5M15 9l5.25-5.25M15 15h4.5M15 15v4.5m0-4.5l5.25 5.25" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                </svg>
              )}
            </button>
          </div>
        </>
      ) : (
        <div className="absolute inset-0 flex flex-col items-center justify-center text-white bg-gradient-to-t from-black/60 to-transparent">
          <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-md mb-4">
            <svg className="w-10 h-10" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
            </svg>
          </div>
          <p className="text-sm opacity-80">영상을 업로드하면 여기에 표시됩니다</p>
        </div>
      )}
    </div>
  );
}
