"""Chainlit UI 실행 스크립트"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Chainlit import 및 실행
if __name__ == "__main__":
    import subprocess

    print("="*60)
    print("로그 분석 시스템 UI 시작")
    print("="*60)
    print("\n브라우저가 자동으로 열립니다...")
    print("종료하려면 Ctrl+C를 누르세요.\n")

    # Chainlit 실행
    subprocess.run([
        "chainlit", "run", "src/ui/app.py", "-w"
    ])