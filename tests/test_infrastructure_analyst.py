"""Infrastructure Analyst Agent 테스트"""

from __future__ import annotations

import sys
from pathlib import Path

# UTF-8 출력 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.infrastructure_analyst import InfrastructureAnalystAgent
from src.agents.classifier import ClassificationAgent
from src.agents.log_parser import LogParserAgent


def test_db_connection_failure_analysis():
    """시나리오 1: DB 연결 실패 심층 분석"""
    print("=== Test 1: DB 연결 실패 심층 분석 ===")

    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다: {test_file}")
        return

    # 로그 파싱
    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()
    print("✓ 로그 파싱 완료")

    # 분류
    classifier = ClassificationAgent()
    classification = classifier.classify(log_data)
    print(f"✓ 분류 완료: {classification['category']}")

    # 심층 분석
    analyst = InfrastructureAnalystAgent()
    analysis = analyst.analyze(log_data, classification)
    print(f"✓ 분석 완료")

    # 결과 검증
    print(f"\n이슈 유형: {analysis['issue_type']}")
    print(f"긴급도: {analysis['urgency']}")
    print(f"영향받는 컴포넌트 수: {len(analysis['affected_components'])}")
    print(f"권장 조치사항 수: {len(analysis['recommended_actions'])}")

    # 필수 필드 확인
    assert analysis['issue_type'], "이슈 유형이 비어있습니다"
    assert analysis['root_cause'], "근본 원인이 비어있습니다"
    assert analysis['impact_analysis'], "영향 분석이 비어있습니다"
    assert len(analysis['affected_components']) > 0, "영향받는 컴포넌트가 없습니다"
    assert len(analysis['recommended_actions']) > 0, "권장 조치사항이 없습니다"
    assert analysis['urgency'] in ['immediate', 'urgent', 'medium', 'low'], \
        f"유효하지 않은 긴급도: {analysis['urgency']}"

    # DB 연결 실패는 immediate 또는 urgent여야 함
    assert analysis['urgency'] in ['immediate', 'urgent'], \
        f"DB 연결 실패는 immediate 또는 urgent여야 합니다 (현재: {analysis['urgency']})"

    print("✓ 모든 검증 통과")


def test_analysis_result_structure():
    """분석 결과 구조 검증"""
    print("\n=== Test 2: 분석 결과 구조 검증 ===")

    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()

    analyst = InfrastructureAnalystAgent()
    analysis = analyst.analyze(log_data)

    # 필수 필드 존재 확인
    required_fields = [
        'issue_type',
        'root_cause',
        'impact_analysis',
        'affected_components',
        'recommended_actions',
        'urgency',
        'estimated_recovery_time'
    ]

    for field in required_fields:
        assert field in analysis, f"필수 필드 누락: {field}"

    # 타입 검증
    assert isinstance(analysis['issue_type'], str), "issue_type은 문자열이어야 합니다"
    assert isinstance(analysis['root_cause'], str), "root_cause는 문자열이어야 합니다"
    assert isinstance(analysis['impact_analysis'], str), "impact_analysis는 문자열이어야 합니다"
    assert isinstance(analysis['affected_components'], list), "affected_components는 리스트여야 합니다"
    assert isinstance(analysis['recommended_actions'], list), "recommended_actions는 리스트여야 합니다"

    # 긴급도 값 검증
    valid_urgencies = ['immediate', 'urgent', 'medium', 'low']
    assert analysis['urgency'] in valid_urgencies, \
        f"유효하지 않은 긴급도: {analysis['urgency']}"

    print(f"✓ 모든 필드 검증 완료")
    print(f"  필수 필드: {', '.join(required_fields)}")
    print(f"  이슈 유형: {analysis['issue_type']}")
    print(f"  긴급도: {analysis['urgency']} (유효함)")
    print(f"  권장 조치사항: {len(analysis['recommended_actions'])}개")


def test_detailed_output():
    """상세 출력 테스트"""
    print("\n=== Test 3: 상세 분석 결과 출력 ===")

    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    # 전체 파이프라인 실행
    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()

    classifier = ClassificationAgent()
    classification = classifier.classify(log_data)

    analyst = InfrastructureAnalystAgent()
    analysis = analyst.analyze(log_data, classification)

    # 상세 출력
    print(f"\n{'='*60}")
    print("📊 분석 결과")
    print(f"{'='*60}")

    print(f"\n🔍 이슈 유형: {analysis['issue_type']}")

    print(f"\n💡 근본 원인:")
    print(f"  {analysis['root_cause'][:150]}...")

    print(f"\n📈 영향 분석:")
    print(f"  {analysis['impact_analysis'][:150]}...")

    print(f"\n⚠️  영향받는 컴포넌트:")
    for component in analysis['affected_components'][:5]:  # 처음 5개만
        print(f"  - {component}")

    print(f"\n🔧 권장 조치사항:")
    for i, action in enumerate(analysis['recommended_actions'][:5], 1):  # 처음 5개만
        print(f"  {i}. {action[:100]}...")

    print(f"\n⏰ 긴급도: {analysis['urgency']}")
    print(f"⏱️  예상 복구 시간: {analysis['estimated_recovery_time']}")

    print(f"\n✓ 상세 출력 완료")


if __name__ == "__main__":
    try:
        print("Infrastructure Analyst Agent 테스트 시작\n")
        print("⚠️  이 테스트는 LLM API를 호출합니다.")
        print("⚠️  .env 파일에 API 키가 설정되어 있어야 합니다.\n")

        test_analysis_result_structure()
        test_db_connection_failure_analysis()
        test_detailed_output()

        print("\n" + "=" * 60)
        print("모든 테스트 통과! ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
    except Exception as e:
        print(f"\n[ERROR] 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()
