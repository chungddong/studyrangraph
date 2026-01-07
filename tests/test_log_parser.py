"""Log Parser Agent 테스트"""

from __future__ import annotations

import sys
from pathlib import Path

# UTF-8 출력 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.log_parser import LogParserAgent


def test_basic_parsing():
    """기본 파싱 테스트"""
    print("=== Test 1: 기본 파싱 테스트 ===")

    parser = LogParserAgent()
    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
        return

    logs = parser.parse_file(test_file)

    assert len(logs) > 0, "로그가 파싱되지 않았습니다"
    print(f"✓ {len(logs)}개의 로그 파싱 완료")

    # 첫 번째 로그 확인
    first_log = logs[0]
    assert 'timestamp' in first_log
    assert 'level' in first_log
    assert 'message' in first_log
    assert 'raw' in first_log
    assert 'line_number' in first_log
    print(f"✓ 로그 구조 검증 완료")
    print(f"  첫 번째 로그: {first_log['raw']}")


def test_statistics():
    """통계 생성 테스트"""
    print("\n=== Test 2: 통계 생성 테스트 ===")

    parser = LogParserAgent()
    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
        return

    parser.parse_file(test_file)
    stats = parser.get_statistics()

    assert stats is not None, "통계가 생성되지 않았습니다"
    print(f"✓ 통계 생성 완료")
    print(f"  총 라인: {stats['total_lines']}")
    print(f"  ERROR: {stats['error_count']}")
    print(f"  WARN: {stats['warn_count']}")
    print(f"  INFO: {stats['info_count']}")
    print(f"  시간 범위: {stats['time_range']['start']} ~ {stats['time_range']['end']}")

    if stats['error_patterns']:
        print(f"  에러 패턴:")
        for pattern, count in stats['error_patterns'].items():
            print(f"    - {pattern}: {count}건")


def test_filtering():
    """로그 필터링 테스트"""
    print("\n=== Test 3: 로그 필터링 테스트 ===")

    parser = LogParserAgent()
    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
        return

    parser.parse_file(test_file)

    # 에러 로그 필터링
    error_logs = parser.get_error_logs()
    print(f"✓ ERROR 로그: {len(error_logs)}건")
    if error_logs:
        print(f"  예시: {error_logs[0]['message'][:80]}")

    # 키워드 검색
    database_logs = parser.get_logs_with_keyword("database")
    print(f"✓ 'database' 키워드: {len(database_logs)}건")

    connection_logs = parser.get_logs_with_keyword("connection")
    print(f"✓ 'connection' 키워드: {len(connection_logs)}건")


def test_llm_format():
    """LLM 포맷 출력 테스트"""
    print("\n=== Test 4: LLM 포맷 출력 테스트 ===")

    parser = LogParserAgent()
    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
        return

    parser.parse_file(test_file)
    llm_output = parser.format_for_llm()

    assert len(llm_output) > 0, "LLM 포맷 출력이 비어있습니다"
    print(f"✓ LLM 포맷 생성 완료 ({len(llm_output)} 글자)")

    # 처음 500자만 출력
    print(f"\n{llm_output[:500]}...")


def test_multiple_scenarios():
    """여러 시나리오 테스트"""
    print("\n=== Test 5: 여러 시나리오 파싱 테스트 ===")

    scenarios = [
        "scenario-01-db-connection-failure/dataset-01.log",
        "scenario-02-xss-attack/dataset-01.log",
        "scenario-03-n-plus-one-query/dataset-01.log",
    ]

    for scenario in scenarios:
        test_file = project_root / "datasets" / scenario

        if not test_file.exists():
            print(f"[SKIP] {scenario}")
            continue

        parser = LogParserAgent()
        logs = parser.parse_file(test_file)
        stats = parser.get_statistics()

        print(f"\n✓ {scenario}")
        print(f"  라인: {len(logs)}, ERROR: {stats['error_count']}, WARN: {stats['warn_count']}")


if __name__ == "__main__":
    try:
        test_basic_parsing()
        test_statistics()
        test_filtering()
        test_llm_format()
        test_multiple_scenarios()

        print("\n" + "=" * 50)
        print("모든 테스트 통과! ✓")
        print("=" * 50)

    except AssertionError as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
    except Exception as e:
        print(f"\n[ERROR] 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()