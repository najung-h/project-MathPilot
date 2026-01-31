"""
Test NVIDIA NIM API Connection
"""

import asyncio
import sys
import os
from pathlib import Path

# backend 경로 추가
sys.path.append(str(Path("backend").resolve()))

# .env 로드
from dotenv import load_dotenv
load_dotenv(Path("backend/.env"))

from app.services.llm.nvidia_client import NvidiaClient
from app.config import settings

async def test_nvidia():
    print(f"[TEST] NVIDIA_API_KEY present: {bool(settings.NVIDIA_API_KEY)}")
    if not settings.NVIDIA_API_KEY:
        print("[ERROR] No NVIDIA_API_KEY found.")
        return

    client = NvidiaClient(api_key=settings.NVIDIA_API_KEY)
    
    # 1. Text Generation Test
    print("\n[TEST] 1. Text Generation (Llama 3.3 70B)...")
    try:
        response = await client.chat([{"role": "user", "content": "Hello, are you working?"}])
        print(f"  -> Response: {response}")
    except Exception as e:
        print(f"  -> FAILED: {e}")

    # 2. Vision Test
    print("\n[TEST] 2. Vision Analysis (Llama 3.2 90B)...")
    try:
        # Full HD (1920x1080) 더미 이미지 생성
        import cv2
        import numpy as np
        print("  -> Creating Full HD (1920x1080) dummy image...")
        img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        # 이미지에 랜덤 노이즈 추가 (압축률 낮추기 위해)
        cv2.randn(img, 0, 255)
        
        _, img_bytes = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        print(f"  -> Image size: {len(img_bytes) / 1024:.2f} KB")
        
        response = await client.analyze_image(
            image_bytes=img_bytes.tobytes(),
            prompt="What is in this image?"
        )
        print(f"  -> Response: {response}")
    except Exception as e:
        print(f"  -> FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_nvidia())
