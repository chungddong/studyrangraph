"""Classification Agent - 로그 카테고리 분류 및 라우팅"""

from __future__ import annotations

from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.llm_provider import get_llm


# 분류 카테고리 타입
CategoryType = Literal["infrastructure", "security", "performance", "application", "user"]


class ClassificationResult(TypedDict):
    """분류 결과 구조"""
    category: CategoryType
    confidence: str  # high, medium, low
    reason: str
    severity: str  # critical, high, medium, low
    key_indicators: list[str]


class ClassificationAgent:
    """로그 분석 후 적절한 카테고리로 분류하는 에이전트

    카테고리:
    - infrastructure: 데이터베이스, 네트워크, 서버 관련
    - security: 인증, 권한, XSS, SQL Injection, 무차별 대입 공격
    - performance: 응답 시간, N+1 쿼리, 메모리 누수
    - application: 비즈니스 로직 오류
    - user: 잘못된 입력, 비정상적인 행동 패턴
    """

    SYSTEM_PROMPT = """당신은 로그 분석 전문가입니다.
주어진 로그를 분석하여 이슈의 카테고리를 정확하게 분류해야 합니다.

## 분류 카테고리

1. **infrastructure** (인프라)
   - 데이터베이스 연결 장애, 서비스 중단
   - 네트워크 오류, 타임아웃
   - 서버 리소스 고갈 (메모리, CPU, 디스크)
   - 시스템 레벨 에러

2. **security** (보안)
   - 인증/권한 오류 (401, 403)
   - XSS 공격 시도 (스크립트 태그 삽입)
   - SQL Injection 시도
   - 무차별 대입 공격 (Brute Force)
   - 비정상적인 요청 패턴
   - 보안 필터 작동

3. **performance** (성능)
   - N+1 쿼리 문제
   - 느린 응답 시간 (Slow Query)
   - 메모리 누수
   - 과도한 쿼리 실행
   - 리소스 병목

4. **application** (애플리케이션)
   - 비즈니스 로직 오류
   - 데이터 검증 실패 (400 에러)
   - 애플리케이션 코드 버그
   - 예외 처리 누락

5. **user** (사용자)
   - 잘못된 사용자 입력
   - 비정상적인 사용 패턴
   - 사용자 오류로 인한 400 에러

## 심각도 레벨

- **critical**: 시스템 전체에 영향, 즉시 조치 필요
- **high**: 주요 기능 장애, 빠른 조치 필요
- **medium**: 부분적 기능 저하, 모니터링 필요
- **low**: 경미한 이슈, 정기 점검 시 해결

## 응답 형식

반드시 다음 형식의 JSON으로 응답하세요:

{
  "category": "infrastructure | security | performance | application | user",
  "confidence": "high | medium | low",
  "reason": "분류 이유를 1-2문장으로 설명",
  "severity": "critical | high | medium | low",
  "key_indicators": ["주요 근거 1", "주요 근거 2", "주요 근거 3"]
}

## 분류 예시

**Example 1: Database 연결 실패**
- Category: infrastructure
- Severity: critical
- Key indicators: ECONNREFUSED, 모든 API 500 에러, Database connection error

**Example 2: XSS 공격**
- Category: security
- Severity: high
- Key indicators: <script> 태그, 동일 사용자 반복 시도, Dangerous HTML content detected

**Example 3: N+1 쿼리**
- Category: performance
- Severity: medium
- Key indicators: 반복 쿼리 실행, Slow query warning, 1000ms+ 응답시간

**Example 4: 무차별 대입 공격**
- Category: security
- Severity: high
- Key indicators: 동일 IP 반복 로그인 실패, 401 에러 다수, 짧은 시간 내 대량 요청
"""

    def __init__(self):
        self.llm = get_llm(temperature=0.0)  # 일관된 분류를 위해 temperature=0

    def classify(self, log_data: str) -> ClassificationResult:
        """로그 데이터를 분석하여 카테고리 분류

        Args:
            log_data: 로그 데이터 (보통 LogParser.format_for_llm() 결과)

        Returns:
            분류 결과 (카테고리, 신뢰도, 이유, 심각도, 주요 지표)
        """
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"다음 로그를 분석하여 카테고리를 분류해주세요:\n\n{log_data}")
        ]

        response = self.llm.invoke(messages)
        result_text = response.content

        # JSON 파싱
        import json
        import re

        # JSON 블록 추출 (마크다운 코드 블록 제거)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(1)
        else:
            # 코드 블록 없이 바로 JSON인 경우
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group(0)

        try:
            result = json.loads(result_text)

            return ClassificationResult(
                category=result.get('category', 'application'),
                confidence=result.get('confidence', 'medium'),
                reason=result.get('reason', ''),
                severity=result.get('severity', 'medium'),
                key_indicators=result.get('key_indicators', [])
            )
        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 기본값 반환
            print(f"[WARN] JSON 파싱 실패: {e}")
            print(f"[WARN] 원본 응답: {result_text[:200]}...")

            return ClassificationResult(
                category='application',
                confidence='low',
                reason='LLM 응답 파싱 실패',
                severity='medium',
                key_indicators=['파싱 오류']
            )

    def get_routing_decision(self, classification: ClassificationResult) -> str:
        """분류 결과를 바탕으로 어떤 Analyst Agent로 라우팅할지 결정

        Args:
            classification: 분류 결과

        Returns:
            라우팅할 에이전트 이름
        """
        category = classification['category']

        routing_map = {
            'infrastructure': 'infrastructure_analyst',
            'security': 'security_analyst',
            'performance': 'performance_analyst',
            'application': 'application_analyst',
            'user': 'application_analyst',  # user 이슈는 application에서 처리
        }

        return routing_map.get(category, 'infrastructure_analyst')


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

    print("=== Classification Agent 테스트 ===\n")

    # 테스트할 시나리오 파일들
    test_scenarios = [
        ("시나리오 1: DB 연결 실패", "datasets/scenario-01-db-connection-failure/dataset-01.log"),
        ("시나리오 2: XSS 공격", "datasets/scenario-02-xss-attack/dataset-01.log"),
        ("시나리오 3: N+1 쿼리", "datasets/scenario-03-n-plus-one-query/dataset-01.log"),
    ]

    classifier = ClassificationAgent()

    for scenario_name, log_file in test_scenarios:
        log_path = project_root / log_file

        if not log_path.exists():
            print(f"[SKIP] {scenario_name} - 파일 없음")
            continue

        print(f"\n{'='*60}")
        print(f"📋 {scenario_name}")
        print(f"{'='*60}")

        # 로그 파싱
        parser = LogParserAgent()
        parser.parse_file(log_path)
        log_data = parser.format_for_llm()

        # 분류 실행
        print("[분석 중...]")
        result = classifier.classify(log_data)

        # 결과 출력
        print(f"\n✓ 분류 완료")
        print(f"  카테고리: {result['category']}")
        print(f"  심각도: {result['severity']}")
        print(f"  신뢰도: {result['confidence']}")
        print(f"  이유: {result['reason']}")
        print(f"  주요 지표:")
        for indicator in result['key_indicators']:
            print(f"    - {indicator}")

        # 라우팅 결정
        routing = classifier.get_routing_decision(result)
        print(f"\n→ 라우팅: {routing}")

    print("\n" + "="*60)
    print("테스트 완료!")
