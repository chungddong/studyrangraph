"""Infrastructure Analyst Agent - 인프라 이슈 심층 분석"""

from __future__ import annotations

from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.llm_provider import get_llm


class AnalysisResult(TypedDict):
    """분석 결과 구조"""
    issue_type: str
    root_cause: str
    impact_analysis: str
    affected_components: list[str]
    recommended_actions: list[str]
    urgency: str  # immediate, urgent, medium, low
    estimated_recovery_time: str


class InfrastructureAnalystAgent:
    """인프라 관련 이슈를 심층 분석하는 에이전트

    담당 영역:
    - 데이터베이스 연결 장애, 쿼리 오류
    - 네트워크 오류, 타임아웃
    - 서버 리소스 고갈 (메모리, CPU, 디스크)
    - 시스템 레벨 에러
    """

    SYSTEM_PROMPT = """당신은 인프라 전문가입니다.
시스템 로그를 분석하여 인프라 관련 문제의 근본 원인을 파악하고 해결 방안을 제시해야 합니다.

## 분석 영역

### 1. 데이터베이스 이슈
- 연결 장애: ECONNREFUSED, timeout, connection pool exhausted
- 쿼리 오류: syntax error, constraint violation
- 성능 저하: slow query, deadlock

### 2. 네트워크 이슈
- 연결 실패: ECONNREFUSED, ETIMEDOUT, EHOSTUNREACH
- DNS 문제: ENOTFOUND
- 방화벽 차단

### 3. 서버 리소스 이슈
- 메모리 누수: heap out of memory, RSS 지속 증가
- CPU 과부하: high CPU usage, event loop lag
- 디스크 용량 부족: ENOSPC

### 4. 시스템 레벨 에러
- 프로세스 크래시: uncaught exception, SIGTERM
- 포트 충돌: EADDRINUSE
- 권한 문제: EACCES, EPERM

## 분석 프로세스

1. **이슈 유형 식별**: 로그 패턴으로 정확한 이슈 분류
2. **근본 원인 분석**: 표면적 증상이 아닌 실제 원인 파악
3. **영향 범위 평가**: 어떤 컴포넌트와 기능이 영향받는지 분석
4. **긴급도 판정**: 즉시/긴급/보통/낮음
5. **복구 시간 추정**: 현실적인 복구 소요 시간
6. **권장 조치사항**: 우선순위별 실행 가능한 해결 방안

## 응답 형식

반드시 다음 형식의 JSON으로 응답하세요:

{
  "issue_type": "구체적인 이슈 유형 (예: Database Connection Failure, Memory Leak)",
  "root_cause": "근본 원인 분석 (2-3문장, 기술적 세부사항 포함)",
  "impact_analysis": "영향 분석 (서비스 장애 범위, 사용자 영향, 비즈니스 임팩트)",
  "affected_components": ["영향받는 컴포넌트1", "컴포넌트2"],
  "recommended_actions": [
    "1. 즉시 조치: 구체적인 명령어나 절차",
    "2. 단기 해결: 임시 방편",
    "3. 장기 해결: 근본적인 개선 방안"
  ],
  "urgency": "immediate | urgent | medium | low",
  "estimated_recovery_time": "예상 복구 시간 (예: 5-10분, 1-2시간)"
}

## 분석 예시

**Example 1: Database Connection Failure**
```json
{
  "issue_type": "Database Connection Failure (ECONNREFUSED)",
  "root_cause": "MariaDB 서비스가 중단되었거나 네트워크 연결이 끊어져 127.0.0.1:3306 포트로의 연결이 거부되고 있습니다. 로그에서 연속적인 ECONNREFUSED 에러와 함께 모든 데이터베이스 의존 API가 500 에러를 반환하는 것으로 보아 DB 서비스 자체가 다운된 것으로 판단됩니다.",
  "impact_analysis": "전체 시스템의 100% 기능 장애. 회원가입, 로그인, 게시글 조회/작성 등 모든 데이터베이스 의존 기능이 중단되었습니다. 사용자는 서비스를 전혀 이용할 수 없는 상태입니다.",
  "affected_components": ["Database Service (MariaDB)", "All API Endpoints", "Authentication System", "Data Access Layer"],
  "recommended_actions": [
    "1. 즉시 조치: DB 서비스 상태 확인 - systemctl status mariadb 또는 docker ps | grep mariadb",
    "2. 즉시 조치: DB 서비스 재시작 - systemctl restart mariadb 또는 docker restart mariadb",
    "3. 단기 해결: DB 연결 설정 검증 (.env 파일의 DB_HOST, DB_PORT 확인)",
    "4. 장기 해결: DB 모니터링 설정 (Prometheus + Grafana 또는 CloudWatch)",
    "5. 장기 해결: Auto-restart 정책 설정 (Docker restart policy 또는 systemd)",
    "6. 장기 해결: Connection pool 설정 최적화 및 health check 구현"
  ],
  "urgency": "immediate",
  "estimated_recovery_time": "5-10분 (서비스 재시작만 필요한 경우)"
}
```

**Example 2: Memory Leak**
```json
{
  "issue_type": "Memory Leak - Progressive Memory Growth",
  "root_cause": "Node.js 프로세스의 메모리 사용량이 시간에 따라 지속적으로 증가하여 85%를 초과했습니다. 로그에서 RSS와 Heap 크기가 계속 증가하는 패턴이 보이며, 특정 기능 사용 후 메모리가 해제되지 않는 것으로 추정됩니다.",
  "impact_analysis": "서버 응답 시간이 점진적으로 느려지고, 메모리 부족으로 인한 프로세스 크래시 위험이 있습니다. 현재 성능 저하가 발생 중이며, 방치 시 서비스 중단으로 이어질 수 있습니다.",
  "affected_components": ["Node.js Process", "Application Performance", "Server Resources"],
  "recommended_actions": [
    "1. 즉시 조치: 프로세스 재시작으로 임시 복구",
    "2. 단기 해결: PM2 auto-restart 설정 (메모리 임계값 기반)",
    "3. 중기 해결: Heap snapshot 수집 및 분석 (node --inspect)",
    "4. 장기 해결: 메모리 프로파일링 수행하여 누수 원인 코드 식별",
    "5. 장기 해결: Event listener 누적, 큰 객체 참조 유지 등 일반적인 누수 패턴 점검"
  ],
  "urgency": "urgent",
  "estimated_recovery_time": "즉시 재시작: 5분, 근본 해결: 1-2일 (분석 및 수정)"
}
```

## 주의사항

- 로그의 시간 순서를 고려하여 이슈 진행 과정을 파악하세요
- 에러 코드와 메시지를 정확히 인용하세요
- 추측이 아닌 로그 기반 사실에 근거한 분석을 제공하세요
- 실행 가능하고 구체적인 조치사항을 제시하세요 (명령어, 설정 파일 경로 등)
- 긴급도는 비즈니스 영향도와 복구 긴급성을 종합적으로 고려하세요
"""

    def __init__(self):
        self.llm = get_llm(temperature=0.0)

    def analyze(self, log_data: str, classification_result: dict | None = None) -> AnalysisResult:
        """인프라 이슈 심층 분석

        Args:
            log_data: 로그 데이터 (LogParser.format_for_llm() 결과)
            classification_result: Classification Agent의 분류 결과 (선택사항)

        Returns:
            분석 결과 (이슈 유형, 근본 원인, 영향 분석, 권장사항 등)
        """
        prompt_parts = ["다음 인프라 로그를 심층 분석해주세요:\n"]

        # 분류 결과가 있으면 컨텍스트로 추가
        if classification_result:
            prompt_parts.append(f"\n[분류 정보]")
            prompt_parts.append(f"카테고리: {classification_result.get('category', 'N/A')}")
            prompt_parts.append(f"심각도: {classification_result.get('severity', 'N/A')}")
            prompt_parts.append(f"주요 지표: {', '.join(classification_result.get('key_indicators', []))}")
            prompt_parts.append("")

        prompt_parts.append(f"\n[로그 데이터]\n{log_data}")

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content="\n".join(prompt_parts))
        ]

        response = self.llm.invoke(messages)
        result_text = response.content

        # JSON 파싱
        import json
        import re

        # JSON 블록 추출
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(0)

        try:
            result = json.loads(result_text)

            return AnalysisResult(
                issue_type=result.get('issue_type', 'Unknown Issue'),
                root_cause=result.get('root_cause', ''),
                impact_analysis=result.get('impact_analysis', ''),
                affected_components=result.get('affected_components', []),
                recommended_actions=result.get('recommended_actions', []),
                urgency=result.get('urgency', 'medium'),
                estimated_recovery_time=result.get('estimated_recovery_time', 'Unknown')
            )
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON 파싱 실패: {e}")
            print(f"[WARN] 원본 응답: {result_text[:200]}...")

            return AnalysisResult(
                issue_type='Analysis Failed',
                root_cause='LLM 응답 파싱 실패',
                impact_analysis='분석 불가',
                affected_components=[],
                recommended_actions=['수동 로그 검토 필요'],
                urgency='medium',
                estimated_recovery_time='Unknown'
            )


# 사용 예시
if __name__ == "__main__":
    import sys
    import io
    from pathlib import Path

    # UTF-8 출력 설정
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 프로젝트 루트 경로 추가
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from src.agents.log_parser import LogParserAgent
    from src.agents.classifier import ClassificationAgent

    print("=== Infrastructure Analyst Agent 테스트 ===\n")

    # 시나리오 1: DB 연결 실패
    test_file = project_root / "datasets/scenario-01-db-connection-failure/dataset-01.log"

    if test_file.exists():
        print("📋 시나리오: DB 연결 실패")
        print("=" * 60)

        # 1. 로그 파싱
        parser = LogParserAgent()
        parser.parse_file(test_file)
        log_data = parser.format_for_llm()
        print("✓ 로그 파싱 완료")

        # 2. 분류
        classifier = ClassificationAgent()
        classification = classifier.classify(log_data)
        print(f"✓ 분류 완료: {classification['category']} (심각도: {classification['severity']})")

        # 3. 심층 분석
        print("\n[분석 중...]")
        analyst = InfrastructureAnalystAgent()
        analysis = analyst.analyze(log_data, classification)

        # 4. 결과 출력
        print(f"\n{'='*60}")
        print("📊 분석 결과")
        print(f"{'='*60}")
        print(f"\n🔍 이슈 유형: {analysis['issue_type']}")
        print(f"\n💡 근본 원인:\n{analysis['root_cause']}")
        print(f"\n📈 영향 분석:\n{analysis['impact_analysis']}")
        print(f"\n⚠️  영향받는 컴포넌트:")
        for component in analysis['affected_components']:
            print(f"  - {component}")
        print(f"\n🔧 권장 조치사항:")
        for i, action in enumerate(analysis['recommended_actions'], 1):
            print(f"  {i}. {action}")
        print(f"\n⏰ 긴급도: {analysis['urgency']}")
        print(f"⏱️  예상 복구 시간: {analysis['estimated_recovery_time']}")

    else:
        print(f"[ERROR] 테스트 파일을 찾을 수 없습니다: {test_file}")
