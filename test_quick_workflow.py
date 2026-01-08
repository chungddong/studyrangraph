"""빠른 워크플로우 테스트 (1개 시나리오만)"""

import sys
import io
from pathlib import Path

# UTF-8 출력
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 프로젝트 루트
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.graph.workflow import analyze_log_file, print_analysis_summary

# DB 연결 실패 시나리오만 테스트
test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

if test_file.exists():
    result = analyze_log_file(str(test_file))
    print_analysis_summary(result)
else:
    print(f"테스트 파일이 없습니다: {test_file}")