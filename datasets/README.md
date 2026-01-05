# 로그 데이터셋

## 폴더 구조

```
datasets/
├── README.md                          # 이 파일
├── scenario-01-db-connection-failure/ # 시나리오 1: DB 연결 장애
│   ├── metadata.json                  # 시나리오 메타데이터
│   ├── dataset-01.log                 # 데이터셋 변형 1
│   ├── dataset-02.log                 # 데이터셋 변형 2
│   └── dataset-03.log                 # 데이터셋 변형 3
├── scenario-02-xss-attack/            # 시나리오 2: XSS 공격
│   ├── metadata.json
│   ├── dataset-01.log
│   ├── dataset-02.log
│   └── dataset-03.log
├── scenario-03-n-plus-one-query/      # 시나리오 3: N+1 쿼리
│   ├── metadata.json
│   ├── dataset-01.log
│   ├── dataset-02.log
│   └── dataset-03.log
├── scenario-04-brute-force-attack/    # 시나리오 4: 무차별 대입 공격
│   ├── metadata.json
│   ├── dataset-01.log
│   ├── dataset-02.log
│   └── dataset-03.log
├── scenario-05-jwt-token-expiry/      # 시나리오 5: JWT 토큰 만료
│   ├── metadata.json
│   ├── dataset-01.log
│   ├── dataset-02.log
│   └── dataset-03.log
├── scenario-06-privilege-escalation/  # 시나리오 6: 권한 상승 시도
│   ├── metadata.json
│   ├── dataset-01.log
│   ├── dataset-02.log
│   └── dataset-03.log
├── scenario-07-memory-leak/           # 시나리오 7: 메모리 누수
│   ├── metadata.json
│   ├── dataset-01.log
│   ├── dataset-02.log
│   └── dataset-03.log
└── scenario-08-validation-failure/    # 시나리오 8: 입력 검증 실패
    ├── metadata.json
    ├── dataset-01.log
    ├── dataset-02.log
    └── dataset-03.log
```

## 데이터셋 변형 전략

각 시나리오마다 3개의 데이터셋 변형을 제공합니다:

- **dataset-01.log**: 기본 시나리오 (명확한 패턴)
- **dataset-02.log**: 혼합 시나리오 (정상 로그 + 이슈 로그)
- **dataset-03.log**: 복합 시나리오 (여러 이슈가 동시에 발생)

## metadata.json 구조

각 시나리오 폴더의 `metadata.json` 파일은 다음 정보를 포함합니다:

```json
{
  "scenario_id": "01",
  "scenario_name": "데이터베이스 연결 장애",
  "severity": "critical",
  "category": "인프라",
  "description": "시나리오 설명",
  "expected_findings": [
    "감지해야 할 항목 1",
    "감지해야 할 항목 2"
  ],
  "recommended_actions": [
    "권장 조치 1",
    "권장 조치 2"
  ],
  "datasets": {
    "dataset-01": {
      "description": "기본 시나리오",
      "log_count": 100,
      "time_span": "5분",
      "issue_density": "높음"
    },
    "dataset-02": {
      "description": "혼합 시나리오",
      "log_count": 500,
      "time_span": "30분",
      "issue_density": "중간"
    },
    "dataset-03": {
      "description": "복합 시나리오",
      "log_count": 1000,
      "time_span": "1시간",
      "issue_density": "낮음"
    }
  }
}
```

## 사용 방법

1. 시나리오 선택
2. 해당 폴더의 `metadata.json` 확인
3. 원하는 데이터셋 변형 선택
4. 로그 파일을 다중 에이전트 시스템에 입력
5. 분석 결과와 예상 결과 비교

## 참고 문서

- [시나리오 문서](../docs/SCENARIOS.md)
- [MNU OUTSIDE API 분석](../docs/MNU_OUTSIDE_API_ANALYSIS.md)
