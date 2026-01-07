# 남은 작업 (Remaining Tasks)

## 현재 완료 상태

### ✅ Phase 1: 기본 환경 설정
- Python 가상환경 생성
- 패키지 설치 (langchain, langgraph, chainlit)
- LLM Provider 추상화 (Claude/Gemini)
- 환경 변수 설정

### ✅ Phase 2: Log Parser Agent
- PM2 로그 포맷 파싱 (정규식)
- 로그 구조화 및 통계 생성
- 필터링 기능 (레벨별, 키워드)
- LLM 전달용 포맷 변환

### ✅ Phase 3: Classification Agent
- LLM 기반 카테고리 자동 분류
- 5가지 카테고리 지원 (infrastructure, security, performance, application, user)
- 심각도 자동 판정 (critical, high, medium, low)
- 라우팅 로직 구현

### ✅ Phase 4: Infrastructure Analyst Agent
- 인프라 이슈 심층 분석
- 근본 원인 파악 및 영향 범위 평가
- 실행 가능한 조치사항 생성 (우선순위별)
- 긴급도 판정 및 복구 시간 추정

### ✅ Phase 5: Security & Performance Analyst Agents
- Security Analyst: XSS, SQL Injection, Brute Force 분석
- Performance Analyst: N+1 쿼리, 느린 응답, 메모리 누수 분석
- 공격 패턴 분석 및 대응 방안 제시
- 병목 분석 및 최적화 계획 수립

---

## 🔴 Phase 6: LangGraph Workflow 통합

### 목표
개별 에이전트들을 LangGraph로 연결하여 자동화된 분석 파이프라인 구축

### 구현 내용

**1. StateGraph 정의** (`src/graph/workflow.py`)
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AnalysisState(TypedDict):
    log_file_path: str
    parsed_logs: dict
    classification: dict
    analysis_result: dict
    final_report: str
```

**2. 노드 함수 구현**
- `parse_logs_node`: LogParser 호출
- `classify_node`: Classifier 호출
- `route_node`: 라우팅 결정 (조건부 엣지)
- `infrastructure_analysis_node`: Infrastructure Analyst 호출
- `security_analysis_node`: Security Analyst 호출
- `performance_analysis_node`: Performance Analyst 호출
- `generate_report_node`: 최종 보고서 생성

**3. 워크플로우 연결**
```python
workflow = StateGraph(AnalysisState)

workflow.add_node("parse", parse_logs_node)
workflow.add_node("classify", classify_node)
workflow.add_node("infrastructure_analysis", infrastructure_analysis_node)
workflow.add_node("security_analysis", security_analysis_node)
workflow.add_node("performance_analysis", performance_analysis_node)
workflow.add_node("generate_report", generate_report_node)

workflow.set_entry_point("parse")
workflow.add_edge("parse", "classify")

# 조건부 라우팅
workflow.add_conditional_edges(
    "classify",
    route_function,
    {
        "infrastructure": "infrastructure_analysis",
        "security": "security_analysis",
        "performance": "performance_analysis"
    }
)

workflow.add_edge("infrastructure_analysis", "generate_report")
workflow.add_edge("security_analysis", "generate_report")
workflow.add_edge("performance_analysis", "generate_report")
workflow.add_edge("generate_report", END)

app = workflow.compile()
```

**4. 테스트 코드** (`tests/test_workflow.py`)
- 3가지 시나리오 전체 파이프라인 테스트
- StateGraph 실행 검증

**예상 소요 시간**: 2-3시간

---

## 🟡 Phase 7: Report Generator Agent

### 목표
분석 결과를 종합하여 읽기 쉬운 최종 보고서 생성

### 구현 내용

**1. Report Generator Agent** (`src/agents/report_generator.py`)
- 분석 결과를 마크다운 보고서로 변환
- Executive Summary (경영진용 요약)
- Technical Details (기술 상세)
- Action Items (우선순위별 조치사항)
- Timeline (예상 복구 시간, 긴급도)

**2. 보고서 템플릿**
```markdown
# 로그 분석 보고서

## 📊 Executive Summary
- 이슈 유형: [...]
- 심각도: [...]
- 예상 영향: [...]

## 🔍 상세 분석
[분석 내용]

## 🔧 권장 조치사항
### 즉시 조치
1. [...]

### 단기 해결
1. [...]

### 장기 개선
1. [...]

## ⏰ Timeline
- 긴급도: [...]
- 예상 복구 시간: [...]
```

**예상 소요 시간**: 1-2시간

---

## 🟢 Phase 8: Chainlit UI 구현

### 목표
사용자가 로그 파일을 업로드하고 분석 결과를 확인할 수 있는 웹 UI

### 구현 내용

**1. Chainlit App** (`src/ui/app.py`)
```python
import chainlit as cl

@cl.on_chat_start
async def start():
    await cl.Message(content="로그 파일을 업로드해주세요.").send()

@cl.on_message
async def main(message: cl.Message):
    # 파일 업로드 처리
    # LangGraph 워크플로우 실행
    # 스트리밍 결과 표시
    pass
```

**2. 주요 기능**
- 로그 파일 업로드 (`.log` 파일)
- 분석 진행 상황 실시간 표시
  - ⏳ 로그 파싱 중...
  - ⏳ 카테고리 분류 중...
  - ⏳ 심층 분석 중...
  - ✓ 분석 완료!
- 최종 보고서 마크다운 렌더링
- 보고서 다운로드 기능 (PDF, Markdown)

**3. 실행 방법**
```bash
chainlit run src/ui/app.py -w
```

**예상 소요 시간**: 3-4시간

---

## 🔵 Phase 9: 추가 기능 (Optional)

### 1. Application Analyst Agent
- 비즈니스 로직 오류 분석
- 데이터 검증 실패 (400 에러) 분석
- 현재는 Application 이슈가 Infrastructure Analyst로 라우팅됨

### 2. 다중 시나리오 일괄 분석
- `datasets/` 폴더의 모든 시나리오 자동 분석
- 비교 보고서 생성

### 3. 로그 스트리밍 지원
- 실시간 로그 모니터링
- Webhook 연동
- 자동 알림

### 4. 대시보드
- 분석 히스토리
- 통계 시각화 (Chart.js, Plotly)
- 이슈 트렌드 분석

---

## 우선순위

### 🔴 High Priority (필수)
1. **Phase 6: LangGraph Workflow** - 전체 시스템 통합에 필수
2. **Phase 8: Chainlit UI** - 사용자 인터페이스 필수

### 🟡 Medium Priority (권장)
3. **Phase 7: Report Generator** - 보고서 품질 향상

### 🟢 Low Priority (선택)
4. **Phase 9: 추가 기능** - 프로젝트 완성도 향상

---

## 다음 단계 제안

**옵션 1: LangGraph 우선 구현**
- 전체 파이프라인을 자동화
- 코드 레벨에서 완전한 시스템 구축
- 이후 Chainlit UI 추가

**옵션 2: Chainlit UI 우선 구현**
- 사용자가 바로 사용 가능한 데모 제작
- 수동 에이전트 호출 방식으로 먼저 구현
- 이후 LangGraph로 자동화

**추천: 옵션 1 (LangGraph 우선)**
- 현재 개별 에이전트가 모두 완성됨
- 자동화된 파이프라인 구축이 자연스러운 다음 단계
- LangGraph 완성 후 Chainlit은 간단히 연결 가능

---

## 참고사항

### API 사용량 관리
- Gemini 무료: 하루 20회 요청 제한
- 개발 중에는 테스트 최소화
- Claude API로 전환 고려 (더 높은 할당량)

### 현재 코드 구조
```
src/
├── agents/
│   ├── log_parser.py ✓
│   ├── classifier.py ✓
│   ├── infrastructure_analyst.py ✓
│   ├── security_analyst.py ✓
│   └── performance_analyst.py ✓
├── graph/
│   └── workflow.py (TODO)
├── utils/
│   └── llm_provider.py ✓
└── ui/
    └── app.py (TODO)
```

### 테스트 커버리지
- ✓ Log Parser 테스트
- ✓ Classifier 테스트
- ✓ Infrastructure Analyst 테스트
- ✓ 통합 테스트 (3개 시나리오)
- ⚠️ Performance 상세 테스트 (API 할당량 초과로 미완료)
