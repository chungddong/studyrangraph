"""LangGraph Workflow - 로그 분석 자동화 파이프라인"""

from __future__ import annotations

from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END

from src.agents.log_parser import LogParserAgent
from src.agents.classifier import ClassificationAgent
from src.agents.infrastructure_analyst import InfrastructureAnalystAgent
from src.agents.security_analyst import SecurityAnalystAgent
from src.agents.performance_analyst import PerformanceAnalystAgent


# State 정의
class AnalysisState(TypedDict):
    """워크플로우 상태"""
    log_file_path: str
    parsed_logs: dict | None
    log_data: str | None
    classification: dict | None
    analysis_result: dict | None
    error: str | None


# 노드 함수들
def parse_logs_node(state: AnalysisState) -> AnalysisState:
    """로그 파싱 노드"""
    print(f"[1/4] 로그 파싱 중: {state['log_file_path']}")

    try:
        parser = LogParserAgent()
        parser.parse_file(state['log_file_path'])

        # 통계 정보 저장
        stats = parser.get_statistics()

        # LLM용 포맷 생성
        log_data = parser.format_for_llm()

        return {
            **state,
            'parsed_logs': stats,
            'log_data': log_data,
            'error': None
        }
    except Exception as e:
        return {
            **state,
            'error': f"로그 파싱 실패: {str(e)}"
        }


def classify_node(state: AnalysisState) -> AnalysisState:
    """분류 노드"""
    print("[2/4] 카테고리 분류 중...")

    if state.get('error'):
        return state

    try:
        classifier = ClassificationAgent()
        classification = classifier.classify(state['log_data'])

        print(f"  → 카테고리: {classification['category']}")
        print(f"  → 심각도: {classification['severity']}")

        return {
            **state,
            'classification': classification,
            'error': None
        }
    except Exception as e:
        return {
            **state,
            'error': f"분류 실패: {str(e)}"
        }


def infrastructure_analysis_node(state: AnalysisState) -> AnalysisState:
    """인프라 분석 노드"""
    print("[3/4] Infrastructure 심층 분석 중...")

    if state.get('error'):
        return state

    try:
        analyst = InfrastructureAnalystAgent()
        analysis = analyst.analyze(
            state['log_data'],
            state['classification']
        )

        print(f"  → 이슈: {analysis['issue_type']}")
        print(f"  → 긴급도: {analysis['urgency']}")

        return {
            **state,
            'analysis_result': analysis,
            'error': None
        }
    except Exception as e:
        return {
            **state,
            'error': f"Infrastructure 분석 실패: {str(e)}"
        }


def security_analysis_node(state: AnalysisState) -> AnalysisState:
    """보안 분석 노드"""
    print("[3/4] Security 심층 분석 중...")

    if state.get('error'):
        return state

    try:
        analyst = SecurityAnalystAgent()
        analysis = analyst.analyze(
            state['log_data'],
            state['classification']
        )

        print(f"  → 공격 유형: {analysis['attack_type']}")
        print(f"  → 심각도: {analysis['severity']}")

        return {
            **state,
            'analysis_result': analysis,
            'error': None
        }
    except Exception as e:
        return {
            **state,
            'error': f"Security 분석 실패: {str(e)}"
        }


def performance_analysis_node(state: AnalysisState) -> AnalysisState:
    """성능 분석 노드"""
    print("[3/4] Performance 심층 분석 중...")

    if state.get('error'):
        return state

    try:
        analyst = PerformanceAnalystAgent()
        analysis = analyst.analyze(
            state['log_data'],
            state['classification']
        )

        print(f"  → 성능 이슈: {analysis['performance_issue']}")

        return {
            **state,
            'analysis_result': analysis,
            'error': None
        }
    except Exception as e:
        return {
            **state,
            'error': f"Performance 분석 실패: {str(e)}"
        }


def application_analysis_node(state: AnalysisState) -> AnalysisState:
    """애플리케이션 분석 노드 (현재는 Infrastructure로 처리)"""
    print("[3/4] Application 분석 중 (Infrastructure Analyst 사용)...")

    # 현재는 Infrastructure Analyst로 처리
    return infrastructure_analysis_node(state)


# 라우팅 함수
def route_to_analyst(state: AnalysisState) -> Literal["infrastructure", "security", "performance", "application", "error"]:
    """분류 결과에 따라 적절한 Analyst로 라우팅"""

    if state.get('error'):
        return "error"

    category = state['classification']['category']

    routing_map = {
        'infrastructure': 'infrastructure',
        'security': 'security',
        'performance': 'performance',
        'application': 'application',
        'user': 'application',  # user 이슈는 application에서 처리
    }

    return routing_map.get(category, 'infrastructure')


def error_node(state: AnalysisState) -> AnalysisState:
    """에러 처리 노드"""
    print(f"[ERROR] {state.get('error', 'Unknown error')}")
    return state


# WorkFlow 구축
def create_workflow() -> StateGraph:
    """로그 분석 워크플로우 생성"""

    workflow = StateGraph(AnalysisState)

    # 노드 추가
    workflow.add_node("parse", parse_logs_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("infrastructure", infrastructure_analysis_node)
    workflow.add_node("security", security_analysis_node)
    workflow.add_node("performance", performance_analysis_node)
    workflow.add_node("application", application_analysis_node)
    workflow.add_node("error", error_node)

    # 엣지 연결
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "classify")

    # 조건부 라우팅 (classify → analyst)
    workflow.add_conditional_edges(
        "classify",
        route_to_analyst,
        {
            "infrastructure": "infrastructure",
            "security": "security",
            "performance": "performance",
            "application": "application",
            "error": "error"
        }
    )

    # 모든 analyst 노드에서 END로
    workflow.add_edge("infrastructure", END)
    workflow.add_edge("security", END)
    workflow.add_edge("performance", END)
    workflow.add_edge("application", END)
    workflow.add_edge("error", END)

    return workflow.compile()


# 편의 함수
def analyze_log_file(log_file_path: str) -> AnalysisState:
    """로그 파일을 분석하는 편의 함수

    Args:
        log_file_path: 분석할 로그 파일 경로

    Returns:
        분석 결과가 포함된 최종 상태
    """
    print("="*60)
    print("로그 분석 파이프라인 시작")
    print("="*60)

    # 워크플로우 생성
    app = create_workflow()

    # 초기 상태
    initial_state: AnalysisState = {
        'log_file_path': log_file_path,
        'parsed_logs': None,
        'log_data': None,
        'classification': None,
        'analysis_result': None,
        'error': None
    }

    # 실행
    final_state = app.invoke(initial_state)

    print("\n" + "="*60)
    print("[4/4] 분석 완료!")
    print("="*60)

    return final_state


def print_analysis_summary(state: AnalysisState):
    """분석 결과 요약 출력"""

    if state.get('error'):
        print(f"\n❌ 분석 실패: {state['error']}")
        return

    print("\n📊 분석 결과 요약")
    print("="*60)

    # 로그 통계
    if state.get('parsed_logs'):
        stats = state['parsed_logs']
        print(f"\n[로그 통계]")
        print(f"  총 라인 수: {stats['total_lines']}")
        print(f"  ERROR: {stats['error_count']}, WARN: {stats['warn_count']}, INFO: {stats['info_count']}")
        print(f"  시간 범위: {stats['time_range']['start']} ~ {stats['time_range']['end']}")

    # 분류 결과
    if state.get('classification'):
        classification = state['classification']
        print(f"\n[분류 결과]")
        print(f"  카테고리: {classification['category']}")
        print(f"  심각도: {classification['severity']}")
        print(f"  신뢰도: {classification['confidence']}")
        print(f"  이유: {classification['reason'][:100]}...")

    # 분석 결과
    if state.get('analysis_result'):
        analysis = state['analysis_result']
        category = state['classification']['category']

        print(f"\n[심층 분석 - {category.upper()}]")

        if category == 'infrastructure':
            print(f"  이슈 유형: {analysis['issue_type']}")
            print(f"  긴급도: {analysis['urgency']}")
            print(f"  근본 원인: {analysis['root_cause'][:100]}...")
            print(f"  권장 조치: {len(analysis['recommended_actions'])}개")

        elif category == 'security':
            print(f"  공격 유형: {analysis['attack_type']}")
            print(f"  심각도: {analysis['severity']}")
            print(f"  공격자: {analysis['attacker_info'].get('identifier', 'N/A')}")
            print(f"  즉시 대응: {len(analysis['immediate_response'])}개")
            print(f"  장기 보안: {len(analysis['recommended_actions'])}개")

        elif category == 'performance':
            print(f"  성능 이슈: {analysis['performance_issue']}")
            print(f"  Quick Wins: {len(analysis['quick_wins'])}개")
            print(f"  최적화 계획: {len(analysis['optimization_plan'])}개")
            print(f"  예상 개선: {analysis['estimated_improvement'][:80]}...")

    print("\n" + "="*60)


# 사용 예시
if __name__ == "__main__":
    import sys
    import io
    from pathlib import Path

    # UTF-8 출력 설정
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 프로젝트 루트
    project_root = Path(__file__).parent.parent.parent

    # 테스트 시나리오
    test_scenarios = [
        ("DB 연결 실패", "datasets/scenario-01-db-connection-failure/dataset-01.log"),
        ("XSS 공격", "datasets/scenario-02-xss-attack/dataset-01.log"),
        ("N+1 쿼리", "datasets/scenario-03-n-plus-one-query/dataset-01.log"),
    ]

    for scenario_name, log_file in test_scenarios:
        log_path = project_root / log_file

        if not log_path.exists():
            print(f"[SKIP] {scenario_name} - 파일 없음")
            continue

        print(f"\n\n{'#'*60}")
        print(f"# 시나리오: {scenario_name}")
        print(f"{'#'*60}\n")

        # 워크플로우 실행
        result = analyze_log_file(str(log_path))

        # 결과 출력
        print_analysis_summary(result)

        # 다음 시나리오 전 대기
        print("\n(다음 시나리오로 이동...)")
        import time
        time.sleep(2)