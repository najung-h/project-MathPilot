"""Text Cleaner - LLM 환각 제거 유틸리티"""

import re


def clean_hallucinations(text: str) -> str:
    """
    LLM 환각으로 인한 반복 텍스트/수식 제거

    Args:
        text: 원본 텍스트

    Returns:
        정제된 텍스트
    """
    if not text:
        return text

    lines = text.split('\n')
    cleaned_lines = []
    prev_line = None

    for line in lines:
        # 1. 한 줄 내에서 같은 패턴이 연속 반복되는 경우 제거
        # 20자 이상 패턴이 2번 이상 연속 반복되면 1번만 남김
        line = re.sub(r'(.{20,}?)\1{2,}', r'\1', line)

        # 2. 연속 중복 줄 제거 (같은 줄이 연속으로 나오면 1개만 유지)
        stripped = line.strip()
        if stripped and stripped == prev_line:
            continue

        # 3. \begin{array}가 한 줄에 3번 이상 → 환각
        if line.count(r'\begin{array}') > 3:
            continue

        # 4. 500자 넘는 줄에 \begin{array} 포함 → 환각 가능성
        if len(line) > 500 and r'\begin{array}' in line:
            continue

        cleaned_lines.append(line)
        if stripped:  # 빈 줄이 아닐 때만 prev_line 업데이트
            prev_line = stripped

    return '\n'.join(cleaned_lines)
