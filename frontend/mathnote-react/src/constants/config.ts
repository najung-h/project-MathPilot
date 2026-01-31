/**
 * 앱 설정 상수
 */

export const APP_CONFIG = {
  // 앱 정보
  APP_NAME: 'MathPilot AI',
  APP_VERSION: '1.0.0',
  APP_DESCRIPTION: '강의 혁신 솔루션',
  
  // 업로드 설정
  UPLOAD: {
    MAX_FILE_SIZE_MB: 500,
    ALLOWED_FILE_TYPES: ['video/mp4', 'video/quicktime'], // MP4, MOV
    ALLOWED_EXTENSIONS: ['.mp4', '.mov'],
  },
  
  // 프레임 추출 설정
  FRAME_INTERVAL_OPTIONS: [
    { value: 1, label: '1초 마다 (기본)' },
    { value: 3, label: '3초 마다' },
    { value: 5, label: '5초 마다' },
  ],
  
  // 기본 처리 옵션
  DEFAULT_PROCESS_OPTIONS: {
    frame_interval_sec: 1.0,
    ssim_threshold: 0.85,
  },
  
  // 폴링 간격 (ms)
  POLLING_INTERVAL: 2000,
} as const;

// 네비게이션 링크
export const NAV_LINKS = {
  WELCOME: {
    PROBLEM: '#problem',
    TECH: '#tech',
    OUTPUT: '#output',
    EXPERIENCE: '#experience',
  },
} as const;
