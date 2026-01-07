"""All Analyst Agents 통합 테스트"""

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
from src.agents.classifier import ClassificationAgent
from src.agents.infrastructure_analyst import InfrastructureAnalystAgent
from src.agents.security_analyst import SecurityAnalystAgent
from src.agents.performance_analyst import PerformanceAnalystAgent


def test_full_pipeline_infrastructure():
    """전체 파이프라인 테스트: Infrastructure"""
    print("=== Test 1: Infrastructure 전체 파이프라인 ===")

    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    # 1. 파싱
    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()
    print("✓ Step 1: 로그 파싱 완료")

    # 2. 분류
    classifier = ClassificationAgent()
    classification = classifier.classify(log_data)
    print(f"✓ Step 2: 분류 완료 - {classification['category']}")

    # 3. 라우팅
    routing = classifier.get_routing_decision(classification)
    print(f"✓ Step 3: 라우팅 - {routing}")

    # 4. 심층 분석
    analyst = InfrastructureAnalystAgent()
    analysis = analyst.analyze(log_data, classification)
    print(f"✓ Step 4: 분석 완료 - {analysis['issue_type']}")

    # 검증
    assert classification['category'] == 'infrastructure'
    assert routing == 'infrastructure_analyst'
    assert len(analysis['recommended_actions']) > 0

    print("\n[분석 결과 요약]")
    print(f"  이슈: {analysis['issue_type']}")
    print(f"  긴급도: {analysis['urgency']}")
    print(f"  권장 조치: {len(analysis['recommended_actions'])}개")


def test_full_pipeline_security():
    """전체 파이프라인 테스트: Security"""
    print("\n=== Test 2: Security 전체 파이프라인 ===")

    test_file = project_root / "datasets/scenario-02-xss-attack/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    # 1. 파싱
    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()
    print("✓ Step 1: 로그 파싱 완료")

    # 2. 분류
    classifier = ClassificationAgent()
    classification = classifier.classify(log_data)
    print(f"✓ Step 2: 분류 완료 - {classification['category']}")

    # 3. 라우팅
    routing = classifier.get_routing_decision(classification)
    print(f"✓ Step 3: 라우팅 - {routing}")

    # 4. 심층 분석
    analyst = SecurityAnalystAgent()
    analysis = analyst.analyze(log_data, classification)
    print(f"✓ Step 4: 분석 완료 - {analysis['attack_type']}")

    # 검증
    assert classification['category'] == 'security'
    assert routing == 'security_analyst'
    assert len(analysis['immediate_response']) > 0

    print("\n[분석 결과 요약]")
    print(f"  공격 유형: {analysis['attack_type']}")
    print(f"  심각도: {analysis['severity']}")
    print(f"  즉시 대응: {len(analysis['immediate_response'])}개")
    print(f"  장기 보안: {len(analysis['recommended_actions'])}개")


def test_full_pipeline_performance():
    """전체 파이프라인 테스트: Performance"""
    print("\n=== Test 3: Performance 전체 파이프라인 ===")

    test_file = project_root / "datasets/scenario-03-n-plus-one-query/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    # 1. 파싱
    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()
    print("✓ Step 1: 로그 파싱 완료")

    # 2. 분류
    classifier = ClassificationAgent()
    classification = classifier.classify(log_data)
    print(f"✓ Step 2: 분류 완료 - {classification['category']}")

    # 3. 라우팅
    routing = classifier.get_routing_decision(classification)
    print(f"✓ Step 3: 라우팅 - {routing}")

    # 4. 심층 분석
    analyst = PerformanceAnalystAgent()
    analysis = analyst.analyze(log_data, classification)
    print(f"✓ Step 4: 분석 완료 - {analysis['performance_issue']}")

    # 검증
    assert classification['category'] == 'performance'
    assert routing == 'performance_analyst'
    assert len(analysis['quick_wins']) > 0

    print("\n[분석 결과 요약]")
    print(f"  성능 이슈: {analysis['performance_issue']}")
    print(f"  Quick Wins: {len(analysis['quick_wins'])}개")
    print(f"  최적화 계획: {len(analysis['optimization_plan'])}개")
    print(f"  예상 개선: {analysis['estimated_improvement'][:50]}...")


def test_detailed_security_output():
    """Security 상세 출력"""
    print("\n=== Test 4: Security 상세 분석 출력 ===")

    test_file = project_root / "datasets/scenario-02-xss-attack/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()

    classifier = ClassificationAgent()
    classification = classifier.classify(log_data)

    analyst = SecurityAnalystAgent()
    analysis = analyst.analyze(log_data, classification)

    print(f"\n{'='*60}")
    print("🔒 보안 분석 결과")
    print(f"{'='*60}")

    print(f"\n🎯 공격 유형: {analysis['attack_type']}")
    print(f"\n📋 공격 패턴:")
    print(f"  {analysis['attack_pattern'][:200]}...")

    print(f"\n⚠️  심각도: {analysis['severity']}")

    print(f"\n👤 공격자 정보:")
    for key, value in analysis['attacker_info'].items():
        print(f"  {key}: {value}")

    print(f"\n🚨 즉시 대응 조치:")
    for i, action in enumerate(analysis['immediate_response'][:3], 1):
        print(f"  {i}. {action}")

    print(f"\n🛡️  장기 보안 강화:")
    for i, action in enumerate(analysis['recommended_actions'][:3], 1):
        print(f"  {i}. {action}")


def test_detailed_performance_output():
    """Performance 상세 출력"""
    print("\n=== Test 5: Performance 상세 분석 출력 ===")

    test_file = project_root / "datasets/scenario-03-n-plus-one-query/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    parser = LogParserAgent()
    parser.parse_file(test_file)
    log_data = parser.format_for_llm()

    classifier = ClassificationAgent()
    classification = classifier.classify(log_data)

    analyst = PerformanceAnalystAgent()
    analysis = analyst.analyze(log_data, classification)

    print(f"\n{'='*60}")
    print("⚡ 성능 분석 결과")
    print(f"{'='*60}")

    print(f"\n🎯 성능 이슈: {analysis['performance_issue']}")
    print(f"\n🔍 병목 분석:")
    print(f"  {analysis['bottleneck_analysis'][:200]}...")

    print(f"\n📊 메트릭:")
    for key, value in analysis['metrics'].items():
        print(f"  {key}: {value}")

    print(f"\n⚡ Quick Wins (즉시 적용):")
    for i, action in enumerate(analysis['quick_wins'][:3], 1):
        print(f"  {i}. {action}")

    print(f"\n🎯 최적화 계획 (장기):")
    for i, action in enumerate(analysis['optimization_plan'][:3], 1):
        print(f"  {i}. {action}")

    print(f"\n📈 예상 개선 효과:")
    print(f"  {analysis['estimated_improvement'][:150]}...")


if __name__ == "__main__":
    try:
        print("All Analyst Agents 통합 테스트 시작\n")
        print("⚠️  이 테스트는 LLM API를 호출합니다.")
        print("⚠️  .env 파일에 API 키가 설정되어 있어야 합니다.\n")

        test_full_pipeline_infrastructure()
        test_full_pipeline_security()
        test_full_pipeline_performance()
        test_detailed_security_output()
        test_detailed_performance_output()

        print("\n" + "=" * 60)
        print("모든 테스트 통과! ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
    except Exception as e:
        print(f"\n[ERROR] 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()
