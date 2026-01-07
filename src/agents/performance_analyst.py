"""Performance Analyst Agent - 성능 이슈 심층 분석"""

from __future__ import annotations

from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.llm_provider import get_llm


class PerformanceAnalysisResult(TypedDict):
    """성능 분석 결과 구조"""
    performance_issue: str
    bottleneck_analysis: str
    metrics: dict
    impact_on_users: str
    root_cause: str
    optimization_plan: list[str]
    quick_wins: list[str]
    estimated_improvement: str


class PerformanceAnalystAgent:
    """성능 관련 이슈를 심층 분석하는 에이전트

    담당 영역:
    - N+1 쿼리 문제
    - 느린 응답 시간 (Slow Query)
    - 메모리 누수
    - 과도한 리소스 사용
    - 비효율적인 알고리즘
    """

    SYSTEM_PROMPT = """당신은 성능 최적화 전문가입니다.
시스템 로그를 분석하여 성능 병목을 식별하고 최적화 방안을 제시해야 합니다.

## 분석 영역

### 1. 데이터베이스 성능
- N+1 쿼리: 반복적인 개별 쿼리 실행
- Slow Query: 임계값 초과 쿼리
- 인덱스 부재: Full Table Scan
- 쿼리 최적화: JOIN vs 개별 쿼리

### 2. 응답 시간 성능
- API 응답 지연: >200ms, >1000ms, >5000ms
- 타임아웃: Request timeout, Gateway timeout
- 네트워크 지연: Latency issues
- 동기 처리로 인한 블로킹

### 3. 메모리 성능
- 메모리 누수: 지속적인 메모리 증가
- Heap 부족: Out of Memory
- 가비지 컬렉션 과다: GC overhead
- 대용량 객체 처리: Buffer overflow

### 4. CPU 성능
- CPU 과부하: High CPU usage
- Event Loop Lag: Node.js 이벤트 루프 지연
- 무한 루프: Infinite loop
- 비효율적인 알고리즘: O(n²) vs O(n log n)

### 5. 리소스 병목
- Connection Pool 고갈
- Thread Pool 부족
- 파일 디스크립터 부족
- 동시 요청 처리 한계

## 분석 프로세스

1. **성능 이슈 식별**: 로그에서 성능 지표 추출
2. **병목 분석**: 어디서 시간이 소모되는지 파악
3. **메트릭 수집**: 응답시간, 쿼리 횟수, 리소스 사용량
4. **사용자 영향**: 체감 성능 저하 정도
5. **근본 원인**: 왜 느린지 기술적 원인 분석
6. **최적화 계획**: 단계별 개선 방안

## 응답 형식

반드시 다음 형식의 JSON으로 응답하세요:

{
  "performance_issue": "성능 이슈 유형 (N+1 Query, Slow Response, Memory Leak, etc.)",
  "bottleneck_analysis": "병목 지점 상세 분석 (어디서 시간/리소스가 소모되는지)",
  "metrics": {
    "avg_response_time": "평균 응답 시간",
    "max_response_time": "최대 응답 시간",
    "query_count": "쿼리 실행 횟수",
    "threshold_violations": "임계값 위반 횟수",
    "affected_requests": "영향받은 요청 수"
  },
  "impact_on_users": "사용자 영향 분석 (체감 속도, UX 저하)",
  "root_cause": "근본 원인 (기술적 세부사항)",
  "optimization_plan": [
    "장기 최적화 방안1 (구조적 개선)",
    "장기 최적화 방안2"
  ],
  "quick_wins": [
    "즉시 적용 가능한 개선1 (빠른 효과)",
    "즉시 적용 가능한 개선2"
  ],
  "estimated_improvement": "예상 성능 개선 효과"
}

## 분석 예시

**Example 1: N+1 Query Problem**
```json
{
  "performance_issue": "N+1 Query Problem",
  "bottleneck_analysis": "/api/posts 엔드포인트에서 게시글 목록 조회 시, 먼저 게시글 20개를 조회한 후(1번의 쿼리), 각 게시글의 댓글을 개별적으로 조회(20번의 쿼리)하여 총 21번의 쿼리가 실행됩니다. 이로 인해 응답 시간이 1,234ms ~ 2,845ms로 급증했습니다.",
  "metrics": {
    "avg_response_time": "1,500ms",
    "max_response_time": "2,845ms",
    "query_count": "21-51 queries per request",
    "threshold_violations": "200ms 임계값 위반 100%",
    "affected_requests": "모든 /api/posts 요청"
  },
  "impact_on_users": "게시글 목록 로딩이 2~3초 걸려 사용자가 답답함을 느끼며, 모바일 환경에서는 더 심각한 지연이 발생합니다. 사용자 이탈률이 증가할 수 있습니다.",
  "root_cause": "TypeORM의 relations 설정이 누락되어 있습니다. find() 메서드에서 comments를 eager loading하지 않고, 각 게시글마다 별도로 댓글을 조회하는 lazy loading 방식이 사용되고 있습니다.",
  "optimization_plan": [
    "TypeORM Entity에 @OneToMany relations 설정 추가 (eager: true 옵션)",
    "find({ relations: ['comments'] }) 옵션 사용하여 JOIN 쿼리로 변경",
    "필요한 경우 QueryBuilder를 사용한 최적화된 JOIN 쿼리 작성",
    "데이터베이스 인덱스 추가 (post_id, created_at 등)",
    "pagination 개선 (무한 스크롤 또는 커서 기반 페이징)"
  ],
  "quick_wins": [
    "즉시: find({ relations: ['comments'] }) 한 줄 추가로 N+1 문제 해결",
    "즉시: limit 파라미터 검증 추가 (최대 50개로 제한)",
    "단기: 응답 캐싱 추가 (Redis, 1분 TTL)"
  ],
  "estimated_improvement": "응답 시간 80-90% 감소 예상 (2,845ms → 200-300ms). 21-51개 쿼리 → 1-2개 쿼리로 감소."
}
```

**Example 2: Memory Leak**
```json
{
  "performance_issue": "Memory Leak - Progressive Memory Growth",
  "bottleneck_analysis": "Node.js 프로세스의 RSS와 Heap 크기가 시간에 따라 지속적으로 증가하여 메모리 사용률이 85%를 초과했습니다. 11:15:00부터 11:25:00까지 10분간 메모리가 약 30% 증가(540MB → 720MB)했으며, 이 추세가 계속되면 OOM(Out of Memory) 크래시가 발생할 것으로 예상됩니다.",
  "metrics": {
    "avg_response_time": "점진적 증가 (초기 100ms → 후기 300ms)",
    "max_response_time": "500ms",
    "query_count": "N/A",
    "threshold_violations": "메모리 85% 임계값 초과",
    "affected_requests": "모든 요청 (전체 프로세스 영향)"
  },
  "impact_on_users": "시간이 지날수록 서버 응답이 느려지고, 최악의 경우 프로세스 크래시로 인한 서비스 중단이 발생할 수 있습니다. 사용자는 간헐적인 타임아웃과 오류를 경험하게 됩니다.",
  "root_cause": "메모리 누수의 일반적인 원인: 1) Event Listener가 제거되지 않고 누적, 2) 클로저에 의한 대용량 객체 참조 유지, 3) 전역 변수나 캐시에 데이터가 무한정 쌓임, 4) 타이머/인터벌이 해제되지 않음. 구체적인 원인은 Heap Snapshot 분석이 필요합니다.",
  "optimization_plan": [
    "Heap Snapshot 수집 및 Chrome DevTools로 분석 (node --inspect)",
    "Memory Profiler 실행하여 누수 코드 위치 식별",
    "Event Listener 정리: removeEventListener() 호출 확인",
    "캐시 정책 개선: LRU Cache 도입 및 최대 크기 제한",
    "WeakMap/WeakSet 사용 검토 (자동 가비지 컬렉션)"
  ],
  "quick_wins": [
    "즉시: 프로세스 재시작으로 임시 복구",
    "즉시: PM2 auto-restart 설정 (max_memory_restart: '800M')",
    "단기: 메모리 모니터링 알림 설정 (80% 임계값)",
    "단기: Node.js --max-old-space-size 늘리기 (임시 방편)"
  ],
  "estimated_improvement": "근본 원인 수정 시 메모리 증가 추세 제거. 안정적인 메모리 사용률 유지 (50-60%). 프로세스 안정성 향상."
}
```

## 주의사항

- 실제 측정된 메트릭을 정확히 제시하세요
- 병목 지점을 구체적으로 명시하세요
- Quick Wins와 장기 최적화를 구분하세요
- 예상 개선 효과를 수치로 제시하세요
- 사용자 관점의 영향을 설명하세요
"""

    def __init__(self):
        self.llm = get_llm(temperature=0.0)

    def analyze(self, log_data: str, classification_result: dict | None = None) -> PerformanceAnalysisResult:
        """성능 이슈 심층 분석

        Args:
            log_data: 로그 데이터
            classification_result: Classification Agent의 분류 결과

        Returns:
            성능 분석 결과
        """
        prompt_parts = ["다음 성능 로그를 심층 분석해주세요:\n"]

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

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(0)

        try:
            result = json.loads(result_text)

            return PerformanceAnalysisResult(
                performance_issue=result.get('performance_issue', 'Unknown Issue'),
                bottleneck_analysis=result.get('bottleneck_analysis', ''),
                metrics=result.get('metrics', {}),
                impact_on_users=result.get('impact_on_users', ''),
                root_cause=result.get('root_cause', ''),
                optimization_plan=result.get('optimization_plan', []),
                quick_wins=result.get('quick_wins', []),
                estimated_improvement=result.get('estimated_improvement', 'Unknown')
            )
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON 파싱 실패: {e}")
            print(f"[WARN] 원본 응답: {result_text[:200]}...")

            return PerformanceAnalysisResult(
                performance_issue='Analysis Failed',
                bottleneck_analysis='LLM 응답 파싱 실패',
                metrics={},
                impact_on_users='분석 불가',
                root_cause='분석 불가',
                optimization_plan=['수동 로그 검토 필요'],
                quick_wins=[],
                estimated_improvement='Unknown'
            )


# 사용 예시는 생략 (테스트 코드에서 확인)
