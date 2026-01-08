# 🔍 로그 분석 시스템

AI 기반 자동 로그 분석 시스템 - LangGraph + Chainlit

## 📋 프로젝트 개요

서버 로그 파일을 업로드하면 AI가 자동으로 분석하여 다음을 제공합니다:
- **인프라 이슈 진단**: DB 연결 장애, 서버 오류, 메모리 누수
- **보안 위협 탐지**: XSS 공격, SQL Injection, 무차별 대입 공격
- **성능 병목 분석**: N+1 쿼리, 느린 응답, 리소스 고갈
- **실행 가능한 해결 방안**: 우선순위별 조치사항 제시

## 🏗️ 아키텍처

```
로그 파일 업로드
    ↓
┌─────────────────────────────────┐
│  LangGraph Workflow (자동화)    │
│                                 │
│  Log Parser → Classifier        │
│       ↓                         │
│  [조건부 라우팅]                 │
│  ├→ Infrastructure Analyst      │
│  ├→ Security Analyst            │
│  └→ Performance Analyst         │
│       ↓                         │
│  최종 보고서 생성                │
└─────────────────────────────────┘
    ↓
분석 결과 및 권장사항
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일에 API 키 설정:

```env
# LLM Provider 선택
LLM_PROVIDER=gemini  # 또는 claude

# Google Gemini API Key
GOOGLE_API_KEY=your-google-api-key-here

# 또는 Claude API Key
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# 모델 설정
GEMINI_MODEL=gemini-1.5-pro
CLAUDE_MODEL=claude-3-5-sonnet-20241022
TEMPERATURE=0.0
```

### 3. UI 실행

```bash
# 방법 1: Python 스크립트
python run_ui.py

# 방법 2: Chainlit 직접 실행
chainlit run src/ui/app.py -w
```

브라우저가 자동으로 열리고 `http://localhost:8000`에서 접속 가능합니다.

### 4. 사용 방법

1. 웹 UI에서 📎 클립 아이콘 클릭
2. `.log` 파일 업로드
3. AI가 자동으로 분석 시작
4. 분석 결과 및 권장 조치사항 확인

## 📁 프로젝트 구조

```
studyrangraph/
├── src/
│   ├── agents/              # 분석 에이전트들
│   │   ├── log_parser.py           # 로그 파싱 (정규식)
│   │   ├── classifier.py           # 카테고리 분류 (LLM)
│   │   ├── infrastructure_analyst.py
│   │   ├── security_analyst.py
│   │   └── performance_analyst.py
│   ├── graph/
│   │   └── workflow.py      # LangGraph 워크플로우
│   ├── utils/
│   │   └── llm_provider.py  # LLM 추상화 (Claude/Gemini)
│   └── ui/
│       └── app.py           # Chainlit UI
├── datasets/                # 테스트 로그 데이터
│   ├── scenario-01-db-connection-failure/
│   ├── scenario-02-xss-attack/
│   └── scenario-03-n-plus-one-query/
├── tests/                   # 테스트 코드
├── docs/                    # 문서
│   ├── SCENARIOS.md
│   ├── IMPLEMENTATION_GUIDE.md
│   └── REMAINING_TASKS.md
├── .env                     # 환경 변수 (API 키)
├── requirements.txt         # 패키지 의존성
└── README.md
```

## 🧪 테스트

```bash
# Log Parser 테스트 (LLM 불필요)
python tests/test_log_parser.py

# Classifier 테스트 (LLM 필요)
python tests/test_classifier.py

# Infrastructure Analyst 테스트
python tests/test_infrastructure_analyst.py

# 전체 파이프라인 테스트
python tests/test_all_analysts.py

# Workflow 테스트
python tests/test_workflow.py
```

## 💡 주요 기능

### 1. Log Parser (정규식 기반)
- PM2 로그 포맷 파싱: `[Timestamp] [Level] Message`
- 로그 레벨별 통계 (ERROR, WARN, INFO, DEBUG)
- 에러 패턴 자동 분류
- 비용: $0 (로컬 처리)

### 2. Classifier (LLM 기반)
- 5가지 카테고리 자동 분류
  - Infrastructure, Security, Performance, Application, User
- 심각도 자동 판정 (Critical, High, Medium, Low)
- 주요 지표 추출

### 3. Analyst Agents (전문 분석)

**Infrastructure Analyst**
- DB 연결 장애, 서버 오류, 메모리 누수 분석
- 근본 원인 파악 및 영향 범위 평가
- 긴급도 판정 및 복구 시간 추정

**Security Analyst**
- XSS, SQL Injection, Brute Force 공격 탐지
- 공격 패턴 및 공격자 정보 추출
- 즉각 대응 vs 장기 보안 강화 구분

**Performance Analyst**
- N+1 쿼리, 느린 응답, 리소스 병목 분석
- Quick Wins vs 장기 최적화 구분
- 예상 성능 개선 효과 수치 제시

### 4. LangGraph Workflow
- 완전 자동화 파이프라인
- 조건부 라우팅 (분류 결과 기반)
- 에러 핸들링 및 State 관리

### 5. Chainlit UI
- 로그 파일 업로드
- 분석 진행 상황 실시간 표시
- 마크다운 보고서 렌더링

## 📊 분석 예시

### Infrastructure - DB 연결 실패
```
이슈: Database Connection Failure (ECONNREFUSED)
긴급도: immediate
근본 원인: DB 서비스 중단 또는 네트워크 단절
권장 조치:
  1. systemctl status mysql 실행
  2. systemctl restart mysql로 재시작
  3. 환경 변수 검증
  ...
예상 복구 시간: 5-10분
```

### Security - XSS 공격
```
공격 유형: XSS Attack
공격자: User: hacker123, IP: 192.168.1.250
시도 횟수: 30회
즉각 대응:
  1. 계정 및 IP 즉시 차단
  2. 보안팀 보고
장기 보안:
  1. Rate Limiting 강화
  2. WAF 도입
  3. CSP 헤더 구현
```

### Performance - N+1 쿼리
```
성능 이슈: N+1 Query Problem
병목: 21-51개 쿼리 실행 → 응답시간 2,845ms
Quick Wins:
  1. find({ relations: ['comments'] }) 추가
  2. Redis 캐싱 (1분 TTL)
예상 개선: 80-90% 감소 (2,845ms → 200-300ms)
```

## 🛠️ 기술 스택

- **LangGraph**: 멀티 에이전트 워크플로우
- **LangChain**: LLM 통합 프레임워크
- **Chainlit**: 웹 UI 프레임워크
- **Google Gemini / Claude**: LLM Provider
- **Python 3.12**: 코어 언어

## 📝 라이선스

MIT License

---
