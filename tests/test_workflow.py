"""LangGraph Workflow 테스트"""

from __future__ import annotations

import sys
from pathlib import Path

# UTF-8 출력 설정
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.graph.workflow import create_workflow, analyze_log_file, print_analysis_summary


def test_workflow_creation():
    """워크플로우 생성 테스트"""
    print("=== Test 1: 워크플로우 생성 ===")

    try:
        workflow = create_workflow()
        print("✓ 워크플로우 생성 성공")

        # 노드 확인
        nodes = workflow.get_graph().nodes
        print(f"✓ 노드 수: {len(nodes)}")

        # 필수 노드 확인
        required_nodes = ['parse', 'classify', 'infrastructure', 'security', 'performance']
        for node in required_nodes:
            assert node in nodes, f"필수 노드 누락: {node}"

        print(f"✓ 필수 노드 확인 완료: {', '.join(required_nodes)}")

    except Exception as e:
        print(f"✗ 워크플로우 생성 실패: {e}")
        raise


def test_infrastructure_pipeline():
    """Infrastructure 전체 파이프라인 테스트"""
    print("\n=== Test 2: Infrastructure 파이프라인 ===")

    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    # 워크플로우 실행
    result = analyze_log_file(str(test_file))

    # 검증
    assert result.get('error') is None, f"에러 발생: {result.get('error')}"
    assert result.get('parsed_logs') is not None, "로그 파싱 실패"
    assert result.get('classification') is not None, "분류 실패"
    assert result.get('analysis_result') is not None, "분석 실패"

    # 분류 확인
    assert result['classification']['category'] == 'infrastructure', \
        f"잘못된 분류: {result['classification']['category']}"

    # 분석 결과 확인
    analysis = result['analysis_result']
    assert 'issue_type' in analysis, "이슈 유형 누락"
    assert 'urgency' in analysis, "긴급도 누락"
    assert 'recommended_actions' in analysis, "권장 조치 누락"

    print("✓ Infrastructure 파이프라인 테스트 통과")
    print(f"  - 이슈: {analysis['issue_type']}")
    print(f"  - 긴급도: {analysis['urgency']}")


def test_security_pipeline():
    """Security 전체 파이프라인 테스트"""
    print("\n=== Test 3: Security 파이프라인 ===")

    test_file = project_root / "datasets/scenario-02-xss-attack/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    # 워크플로우 실행
    result = analyze_log_file(str(test_file))

    # 검증
    assert result.get('error') is None, f"에러 발생: {result.get('error')}"
    assert result['classification']['category'] == 'security', \
        f"잘못된 분류: {result['classification']['category']}"

    # 분석 결과 확인
    analysis = result['analysis_result']
    assert 'attack_type' in analysis, "공격 유형 누락"
    assert 'severity' in analysis, "심각도 누락"
    assert 'immediate_response' in analysis, "즉시 대응 누락"

    print("✓ Security 파이프라인 테스트 통과")
    print(f"  - 공격 유형: {analysis['attack_type']}")
    print(f"  - 심각도: {analysis['severity']}")


def test_performance_pipeline():
    """Performance 전체 파이프라인 테스트"""
    print("\n=== Test 4: Performance 파이프라인 ===")

    test_file = project_root / "datasets/scenario-03-n-plus-one-query/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    # 워크플로우 실행
    result = analyze_log_file(str(test_file))

    # 검증
    assert result.get('error') is None, f"에러 발생: {result.get('error')}"
    assert result['classification']['category'] == 'performance', \
        f"잘못된 분류: {result['classification']['category']}"

    # 분석 결과 확인
    analysis = result['analysis_result']
    assert 'performance_issue' in analysis, "성능 이슈 누락"
    assert 'quick_wins' in analysis, "Quick Wins 누락"
    assert 'optimization_plan' in analysis, "최적화 계획 누락"

    print("✓ Performance 파이프라인 테스트 통과")
    print(f"  - 성능 이슈: {analysis['performance_issue']}")
    print(f"  - Quick Wins: {len(analysis['quick_wins'])}개")


def test_state_flow():
    """State 전달 흐름 테스트"""
    print("\n=== Test 5: State 전달 흐름 ===")

    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    result = analyze_log_file(str(test_file))

    # State 각 단계 확인
    print("✓ State 전달 흐름 검증:")
    print(f"  1. log_file_path: {'✓' if result.get('log_file_path') else '✗'}")
    print(f"  2. parsed_logs: {'✓' if result.get('parsed_logs') else '✗'}")
    print(f"  3. log_data: {'✓' if result.get('log_data') else '✗'}")
    print(f"  4. classification: {'✓' if result.get('classification') else '✗'}")
    print(f"  5. analysis_result: {'✓' if result.get('analysis_result') else '✗'}")

    assert all([
        result.get('log_file_path'),
        result.get('parsed_logs'),
        result.get('log_data'),
        result.get('classification'),
        result.get('analysis_result')
    ]), "State 전달 중 누락된 필드가 있습니다"

    print("✓ 모든 State 필드 정상 전달")


def test_full_analysis_summary():
    """전체 분석 결과 요약 테스트"""
    print("\n=== Test 6: 분석 결과 요약 출력 ===")

    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if not test_file.exists():
        print(f"[SKIP] 테스트 파일이 없습니다")
        return

    result = analyze_log_file(str(test_file))

    # 요약 출력
    print_analysis_summary(result)

    print("✓ 분석 결과 요약 출력 완료")


if __name__ == "__main__":
    try:
        print("LangGraph Workflow 테스트 시작\n")
        print("⚠️  이 테스트는 LLM API를 호출합니다.")
        print("⚠️  .env 파일에 API 키가 설정되어 있어야 합니다.")
        print("⚠️  전체 테스트는 약 6-9회의 API 호출이 필요합니다.\n")

        test_workflow_creation()
        test_infrastructure_pipeline()
        test_security_pipeline()
        test_performance_pipeline()
        test_state_flow()
        test_full_analysis_summary()

        print("\n" + "=" * 60)
        print("모든 테스트 통과! ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[ERROR] 테스트 실패: {e}")
    except Exception as e:
        print(f"\n[ERROR] 예상치 못한 에러: {e}")
        import traceback
        traceback.print_exc()