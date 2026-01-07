"""Security Analyst Agent - 보안 이슈 심층 분석"""

from __future__ import annotations

from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.llm_provider import get_llm


class SecurityAnalysisResult(TypedDict):
    """보안 분석 결과 구조"""
    attack_type: str
    attack_pattern: str
    severity: str
    attacker_info: dict
    security_impact: str
    vulnerability_assessment: str
    recommended_actions: list[str]
    immediate_response: list[str]


class SecurityAnalystAgent:
    """보안 관련 이슈를 심층 분석하는 에이전트

    담당 영역:
    - XSS (Cross-Site Scripting) 공격
    - SQL Injection 시도
    - 무차별 대입 공격 (Brute Force)
    - 인증/권한 오류 (401, 403)
    - 비정상적인 요청 패턴
    """

    SYSTEM_PROMPT = """당신은 보안 전문가입니다.
시스템 로그를 분석하여 보안 위협을 식별하고 대응 방안을 제시해야 합니다.

## 분석 영역

### 1. XSS (Cross-Site Scripting) 공격
- 스크립트 태그 삽입: `<script>`, `<img>`, `<svg>`, `javascript:`
- 이벤트 핸들러: `onerror`, `onload`, `onclick`
- Payload 변형: URL 인코딩, 대소문자 변형

### 2. SQL Injection 공격
- SQL 키워드: `UNION`, `SELECT`, `DROP`, `--`, `/**/`
- Boolean-based: `OR 1=1`, `AND 1=1`
- Time-based: `SLEEP()`, `WAITFOR DELAY`

### 3. 무차별 대입 공격 (Brute Force)
- 동일 IP에서 반복적인 로그인 실패
- 짧은 시간 내 대량 요청
- 여러 계정에 대한 시도
- 자동화된 패턴 (일정한 간격)

### 4. 인증/권한 오류
- 401 Unauthorized: 인증 실패, 토큰 만료
- 403 Forbidden: 권한 부족, 접근 거부
- 비정상적인 접근 시도 패턴

### 5. 기타 보안 위협
- Directory Traversal: `../`, `..\\`
- Command Injection: `;`, `|`, `&&`
- Session Hijacking
- CSRF 공격

## 분석 프로세스

1. **공격 유형 식별**: 로그 패턴으로 공격 방법 분류
2. **공격 패턴 분석**: 사용된 페이로드, 공격 벡터, 변형 기법
3. **공격자 정보 추출**: IP, 사용자, 타임스탬프, 타겟
4. **보안 영향 평가**: 공격 성공 여부, 피해 범위, 위험도
5. **취약점 평가**: 현재 방어 체계의 효과성
6. **대응 방안 제시**: 즉각 대응 + 장기 보안 강화

## 응답 형식

반드시 다음 형식의 JSON으로 응답하세요:

{
  "attack_type": "공격 유형 (XSS Attack, SQL Injection, Brute Force, etc.)",
  "attack_pattern": "공격 패턴 상세 분석 (사용된 페이로드, 기법, 변형)",
  "severity": "critical | high | medium | low",
  "attacker_info": {
    "identifier": "공격자 식별 정보 (IP, 사용자명 등)",
    "target_endpoints": ["타겟 엔드포인트1", "엔드포인트2"],
    "attempt_count": "시도 횟수",
    "time_range": "공격 시간 범위"
  },
  "security_impact": "보안 영향 평가 (공격 성공 여부, 피해 범위, 데이터 노출 위험)",
  "vulnerability_assessment": "취약점 평가 (현재 방어 체계 효과성, 잠재적 위험)",
  "recommended_actions": [
    "장기 보안 강화 방안1",
    "장기 보안 강화 방안2"
  ],
  "immediate_response": [
    "즉각 대응 조치1",
    "즉각 대응 조치2"
  ]
}

## 분석 예시

**Example 1: XSS Attack**
```json
{
  "attack_type": "XSS (Cross-Site Scripting) Attack",
  "attack_pattern": "공격자는 다양한 XSS 페이로드를 시도했습니다: 1) <script>alert('XSS')</script> - 기본 스크립트 태그, 2) <img src=x onerror=alert(1)> - 이미지 태그 이벤트 핸들러, 3) javascript:void(0) - JavaScript 프로토콜, 4) <svg onload=alert(1)> - SVG 태그 이벤트. 모든 시도는 htmlSanitizer에 의해 탐지되고 차단되었습니다.",
  "severity": "high",
  "attacker_info": {
    "identifier": "User: hacker123",
    "target_endpoints": ["/api/posts", "/api/comments"],
    "attempt_count": "30+ attempts in 2 minutes",
    "time_range": "14:32:15 - 14:34:18"
  },
  "security_impact": "현재까지 모든 공격이 차단되었으나, 공격자가 우회 기법을 계속 시도 중입니다. htmlSanitizer가 정상 작동하여 XSS 공격이 성공하지 못했지만, 지속적인 공격으로 시스템 리소스가 소모되고 있습니다.",
  "vulnerability_assessment": "htmlSanitizer가 효과적으로 작동 중이나, 1) 사용자 차단 메커니즘이 늦게 작동 (30회 시도 후 차단), 2) Rate limiting 부재, 3) 실시간 알림 부재 등의 보안 정책 개선이 필요합니다.",
  "recommended_actions": [
    "Rate limiting 구현 (동일 사용자/IP의 분당 요청 제한)",
    "WAF (Web Application Firewall) 도입 검토",
    "보안 로그 실시간 모니터링 시스템 구축",
    "CSP (Content Security Policy) 헤더 강화",
    "입력 검증 레이어 추가 (프론트엔드 + 백엔드)"
  ],
  "immediate_response": [
    "공격자 계정 'hacker123' 즉시 영구 차단",
    "동일 패턴의 요청에 대한 자동 차단 규칙 추가",
    "보안팀에 사고 보고 및 로그 백업",
    "다른 사용자의 유사 패턴 검색 (추가 공격자 식별)"
  ]
}
```

**Example 2: Brute Force Attack**
```json
{
  "attack_type": "Brute Force Attack - Login Credential Stuffing",
  "attack_pattern": "공격자는 192.168.1.100 IP에서 45회의 로그인 시도를 35초 내에 수행했습니다. 여러 계정(user1, admin, test 등)에 대해 무작위 비밀번호를 시도하는 전형적인 credential stuffing 패턴입니다. 시도 간격이 일정하여(약 0.8초) 자동화된 공격으로 판단됩니다.",
  "severity": "high",
  "attacker_info": {
    "identifier": "IP: 192.168.1.100",
    "target_endpoints": ["/login"],
    "attempt_count": "45 failed attempts",
    "time_range": "09:15:10 - 09:15:45 (35 seconds)"
  },
  "security_impact": "현재까지 모든 로그인 시도가 실패했으나, 계정 탈취 위험이 있습니다. 서버 리소스 소모 및 정상 사용자의 로그인 지연이 발생할 수 있습니다.",
  "vulnerability_assessment": "1) 로그인 시도 제한이 부재하거나 느슨함 (45회 시도까지 허용), 2) CAPTCHA 미적용, 3) 계정 잠금 정책 부재, 4) IP 기반 차단이 늦게 작동",
  "recommended_actions": [
    "계정 잠금 정책 구현 (5회 실패 시 15분 잠금)",
    "CAPTCHA 도입 (3회 실패 후 활성화)",
    "2FA (Two-Factor Authentication) 도입",
    "IP 기반 Rate Limiting 강화",
    "비정상 로그인 패턴 탐지 알고리즘 구현"
  ],
  "immediate_response": [
    "공격 IP 192.168.1.100 즉시 차단",
    "공격 대상 계정들의 비밀번호 재설정 권고",
    "로그인 실패 알림 발송 (해당 계정 소유자)",
    "방화벽 규칙 업데이트 (유사 패턴 차단)"
  ]
}
```

## 주의사항

- 공격 성공 여부를 명확히 구분하세요 (차단됨 vs 성공)
- 실제 사용된 페이로드를 정확히 인용하세요
- 공격자 식별 정보를 최대한 추출하세요
- 현재 방어 체계의 효과성을 평가하세요
- 즉각 대응과 장기 보안 강화를 구분하여 제시하세요
"""

    def __init__(self):
        self.llm = get_llm(temperature=0.0)

    def analyze(self, log_data: str, classification_result: dict | None = None) -> SecurityAnalysisResult:
        """보안 이슈 심층 분석

        Args:
            log_data: 로그 데이터
            classification_result: Classification Agent의 분류 결과

        Returns:
            보안 분석 결과
        """
        prompt_parts = ["다음 보안 로그를 심층 분석해주세요:\n"]

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

            return SecurityAnalysisResult(
                attack_type=result.get('attack_type', 'Unknown Attack'),
                attack_pattern=result.get('attack_pattern', ''),
                severity=result.get('severity', 'medium'),
                attacker_info=result.get('attacker_info', {}),
                security_impact=result.get('security_impact', ''),
                vulnerability_assessment=result.get('vulnerability_assessment', ''),
                recommended_actions=result.get('recommended_actions', []),
                immediate_response=result.get('immediate_response', [])
            )
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON 파싱 실패: {e}")
            print(f"[WARN] 원본 응답: {result_text[:200]}...")

            return SecurityAnalysisResult(
                attack_type='Analysis Failed',
                attack_pattern='LLM 응답 파싱 실패',
                severity='medium',
                attacker_info={},
                security_impact='분석 불가',
                vulnerability_assessment='분석 불가',
                recommended_actions=['수동 로그 검토 필요'],
                immediate_response=['보안팀에 문의']
            )


# 사용 예시는 생략 (테스트 코드에서 확인)
