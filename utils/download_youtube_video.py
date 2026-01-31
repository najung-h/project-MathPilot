# 사용법

# python download_youtube.py <유튜브_URL> [옵션]


import argparse
import subprocess
from pathlib import Path

def run(cmd: list[str]) -> None:
    print(" ".join(cmd))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        print(p.stdout)
        raise SystemExit(p.returncode)
    print(p.stdout)

def main():
    parser = argparse.ArgumentParser(description="Download full YouTube video as MP4.")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument(
        "-o",
        "--out",
        default=".",
        help="Output path. If it's a file, that filename is used. If it's a directory, saves with title. (default: current dir)",
    )

    args = parser.parse_args()

    # 출력 경로 처리
    out_path = Path(args.out).resolve()
    
    # yt-dlp 명령어 수정
    cmd = [
        "yt-dlp",
        args.url,
        "-f", "bv*+ba/b",             # 최고 화질
        "--merge-output-format", "mp4", # 병합 시 mp4 사용
        "--remux-video", "mp4"          # [중요] 단일 파일이라도 강제로 mp4로 컨테이너 변경
    ]

    if out_path.suffix:
        # 1. 사용자가 특정 파일명(예: my_video.mp4)을 지정한 경우
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cmd.extend(["-o", str(out_path)])
    else:
        # 2. 사용자가 폴더(예: ./downloads)만 지정한 경우 -> 자동 이름 생성
        out_path.mkdir(parents=True, exist_ok=True)
        # 파일명 포맷: "제목 [ID].mp4"
        # %(ext)s는 remux-video 옵션에 의해 자동으로 mp4가 됩니다.
        cmd.extend(["-o", str(out_path / "%(title)s [%(id)s].%(ext)s")])

    # 다운로드 실행
    run(cmd)

if __name__ == "__main__":
    main()

