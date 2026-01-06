# 구현 가이드라인

## 개발 순서 및 체크리스트

---

## Phase 1: 환경 설정 (30분)

### 1-1. Python 가상환경 생성

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 1-2. 패키지 설치

```bash
pip install -r requirements.txt
```

**필수 패키지**:
- `langchain` - LLM 통합
- `langgraph` - 워크플로우 오케스트레이션
- `langchain-openai` - OpenAI 연동
- `chainlit` - UI
- `python-dotenv` - 환경 변수 관리

### 1-3. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일에 추가:
```
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4
TEMPERATURE=0.0
```

### 1-4. 테스트

```bash
python -c "import langchain; import langgraph; print('Success!')"
```

---

## Phase 2: 로그 파서 구현 (1-2시간)

### 목표
원시 로그 텍스트를 구조화된 Python 딕셔너리로 변환

### 파일: `src/utils/log_parser.py`

### 구현 내용

#### 2-1. 단일 로그 라인 파싱

**입력**:
```
[2026-01-05 03:15:22] ERROR Database connection error: ECONNREFUSED
```

**출력**:
```python
{
    "timestamp": "2026-01-05T03:15:22Z",
    "level": "ERROR",
    "message": "Database connection error: ECONNREFUSED",
    "raw": "[2026-01-05 03:15:22] ERROR Database connection error: ECONNREFUSED"
}
```

**힌트**:
```python
import re
from datetime import datetime

def parse_log_line(line: str) -> dict:
    """단일 로그 라인 파싱"""
    # 패턴: [YYYY-MM-DD HH:MM:SS] LEVEL Message
    pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (\w+) (.+)'
    match = re.match(pattern, line)

    if match:
        timestamp, level, message = match.groups()
        return {
            "timestamp": timestamp.replace(' ', 'T') + 'Z',
            "level": level,
            "message": message.strip(),
            "raw": line
        }
    return None
```

#### 2-2. 전체 로그 파일 파싱

**입력**: 로그 파일 경로
**출력**: 파싱된 로그 리스트 + 통계

```python
def parse_log_file(file_path: str) -> dict:
    """로그 파일 전체 파싱"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    parsed_logs = []
    for line in lines:
        parsed = parse_log_line(line.strip())
        if parsed:
            parsed_logs.append(parsed)

    # 통계 계산
    stats = calculate_statistics(parsed_logs)

    return {
        "logs": parsed_logs,
        "statistics": stats
    }
```

#### 2-3. 통계 계산

```python
def calculate_statistics(logs: list) -> dict:
    """로그 통계 계산"""
    total = len(logs)

    # 레벨별 카운트
    level_counts = {}
    for log in logs:
        level = log['level']
        level_counts[level] = level_counts.get(level, 0) + 1

    # 시간 범위
    if logs:
        timestamps = [log['timestamp'] for log in logs]
        time_span = f"{timestamps[0]} ~ {timestamps[-1]}"
    else:
        time_span = "N/A"

    return {
        "total": total,
        "errors": level_counts.get('ERROR', 0),
        "warnings": level_counts.get('WARN', 0),
        "info": level_counts.get('INFO', 0),
        "debug": level_counts.get('DEBUG', 0),
        "time_span": time_span,
        "error_rate": level_counts.get('ERROR', 0) / total if total > 0 else 0
    }
```

### 테스트

```python
# tests/test_log_parser.py
from src.utils.log_parser import parse_log_file

def test_parse_db_failure():
    result = parse_log_file('datasets/scenario-01-db-connection-failure/dataset-01.log')

    assert result['statistics']['total'] > 0
    assert result['statistics']['errors'] > 0
    print(f"✓ Parsed {result['statistics']['total']} logs")
    print(f"✓ Found {result['statistics']['errors']} errors")

if __name__ == '__main__':
    test_parse_db_failure()
```

---

## Phase 3: 분류 에이전트 구현 (2-3시간)

### 목표
로그를 분석해서 문제 유형(인프라/보안/성능/애플리케이션)과 심각도 판단

### 파일: `src/agents/classifier.py`

### 구현 내용

#### 3-1. 프롬프트 템플릿 작성

```python
from langchain_core.prompts import ChatPromptTemplate

CLASSIFICATION_PROMPT = """당신은 로그 분석 전문가입니다.
다음 로그 통계와 샘플을 보고 문제 유형과 심각도를 판단하세요.

=== 통계 ===
총 로그 수: {total}
에러 수: {errors}
경고 수: {warnings}
에러 비율: {error_rate:.1%}

=== 샘플 로그 (최근 10개) ===
{sample_logs}

=== 분석 요청 ===
다음 항목을 JSON 형식으로 반환하세요:
1. category: "infrastructure" | "security" | "performance" | "application"
2. severity: "critical" | "high" | "medium" | "low"
3. confidence: 0.0 ~ 1.0
4. reasoning: 판단 근거 (한 문장)

예시:
{{
  "category": "infrastructure",
  "severity": "critical",
  "confidence": 0.95,
  "reasoning": "연속적인 데이터베이스 연결 실패 감지"
}}
"""
```

#### 3-2. 분류 에이전트 클래스

```python
from langchain_openai import ChatOpenAI
import json

class ClassificationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.0
        )
        self.prompt = ChatPromptTemplate.from_template(CLASSIFICATION_PROMPT)

    def classify(self, parsed_logs: list, statistics: dict) -> dict:
        """로그 분류"""
        # 샘플 로그 추출 (최근 10개)
        sample_logs = "\n".join([
            f"{log['timestamp']} [{log['level']}] {log['message']}"
            for log in parsed_logs[-10:]
        ])

        # 프롬프트 생성
        messages = self.prompt.format_messages(
            total=statistics['total'],
            errors=statistics['errors'],
            warnings=statistics['warnings'],
            error_rate=statistics['error_rate'],
            sample_logs=sample_logs
        )

        # LLM 호출
        response = self.llm.invoke(messages)

        # JSON 파싱
        try:
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            # 파싱 실패 시 기본값
            return {
                "category": "application",
                "severity": "medium",
                "confidence": 0.5,
                "reasoning": "분류 실패"
            }
```

### 테스트

```python
# tests/test_classifier.py
from src.utils.log_parser import parse_log_file
from src.agents.classifier import ClassificationAgent

def test_classify_db_failure():
    # 로그 파싱
    result = parse_log_file('datasets/scenario-01-db-connection-failure/dataset-01.log')

    # 분류
    classifier = ClassificationAgent()
    classification = classifier.classify(result['logs'], result['statistics'])

    print(f"Category: {classification['category']}")
    print(f"Severity: {classification['severity']}")
    print(f"Confidence: {classification['confidence']}")
    print(f"Reasoning: {classification['reasoning']}")

    assert classification['category'] == 'infrastructure'
    assert classification['severity'] == 'critical'

if __name__ == '__main__':
    test_classify_db_failure()
```

---

## Phase 4: 인프라 분석 에이전트 구현 (2-3시간)

### 목표
인프라 관련 이슈를 상세 분석

### 파일: `src/agents/infrastructure_analyst.py`

### 구현 내용

#### 4-1. 분석 프롬프트

```python
INFRASTRUCTURE_ANALYSIS_PROMPT = """당신은 인프라 문제 분석 전문가입니다.

=== 로그 데이터 ===
{logs}

=== 분석 요청 ===
다음 항목을 JSON 형식으로 반환하세요:

{{
  "issue_type": "문제 유형 (예: Database Connection Failure)",
  "severity": "critical | high | medium | low",
  "first_occurrence": "최초 발생 시간",
  "affected_components": ["영향받은 컴포넌트 목록"],
  "error_count": 에러 발생 횟수,
  "pattern": "발견된 패턴 설명",
  "root_cause": "예상되는 근본 원인",
  "impact": {{
    "service_availability": "서비스 가용성 (%)",
    "affected_users": "영향받은 사용자 범위",
    "data_loss_risk": "데이터 손실 위험 (high/medium/low/none)"
  }},
  "recommendations": [
    "권장 조치 1",
    "권장 조치 2",
    "권장 조치 3"
  ]
}}
"""
```

#### 4-2. 분석 에이전트 클래스

```python
class InfrastructureAnalyst:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0.0)
        self.prompt = ChatPromptTemplate.from_template(INFRASTRUCTURE_ANALYSIS_PROMPT)

    def analyze(self, parsed_logs: list) -> dict:
        """인프라 이슈 분석"""
        # 로그를 텍스트로 변환
        logs_text = "\n".join([
            f"{log['timestamp']} [{log['level']}] {log['message']}"
            for log in parsed_logs
        ])

        # LLM 호출
        messages = self.prompt.format_messages(logs=logs_text)
        response = self.llm.invoke(messages)

        # JSON 파싱
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"error": "분석 실패"}
```

### 테스트

```python
# tests/test_infrastructure_analyst.py
from src.utils.log_parser import parse_log_file
from src.agents.infrastructure_analyst import InfrastructureAnalyst

def test_analyze_db_failure():
    # 로그 파싱
    result = parse_log_file('datasets/scenario-01-db-connection-failure/dataset-01.log')

    # 분석
    analyst = InfrastructureAnalyst()
    analysis = analyst.analyze(result['logs'])

    print(json.dumps(analysis, indent=2, ensure_ascii=False))

    assert 'issue_type' in analysis
    assert 'recommendations' in analysis

if __name__ == '__main__':
    test_analyze_db_failure()
```

---

## Phase 5: LangGraph 워크플로우 구성 (2-3시간)

### 목표
에이전트들을 연결하여 자동화된 분석 파이프라인 구축

### 파일: `src/graph/workflow.py`

### 구현 내용

#### 5-1. State 정의

```python
from typing import TypedDict, List, Dict

class AnalysisState(TypedDict):
    # 입력
    log_file_path: str

    # 파싱 결과
    parsed_logs: List[Dict]
    statistics: Dict

    # 분류 결과
    classification: Dict

    # 분석 결과
    analysis: Dict

    # 최종 보고서
    report: str
```

#### 5-2. 노드 함수 정의

```python
from langgraph.graph import StateGraph, END
from src.utils.log_parser import parse_log_file
from src.agents.classifier import ClassificationAgent
from src.agents.infrastructure_analyst import InfrastructureAnalyst

def parse_logs_node(state: AnalysisState) -> AnalysisState:
    """로그 파싱 노드"""
    result = parse_log_file(state['log_file_path'])
    return {
        "parsed_logs": result['logs'],
        "statistics": result['statistics']
    }

def classify_node(state: AnalysisState) -> AnalysisState:
    """분류 노드"""
    classifier = ClassificationAgent()
    classification = classifier.classify(
        state['parsed_logs'],
        state['statistics']
    )
    return {"classification": classification}

def analyze_infrastructure_node(state: AnalysisState) -> AnalysisState:
    """인프라 분석 노드"""
    analyst = InfrastructureAnalyst()
    analysis = analyst.analyze(state['parsed_logs'])
    return {"analysis": analysis}

def generate_report_node(state: AnalysisState) -> AnalysisState:
    """보고서 생성 노드"""
    report = f"""
# 로그 분석 보고서

## 요약
- **문제 유형**: {state['classification']['category']}
- **심각도**: {state['classification']['severity']}
- **총 로그 수**: {state['statistics']['total']}
- **에러 수**: {state['statistics']['errors']}

## 상세 분석
{state['analysis'].get('issue_type', 'N/A')}

## 권장 조치
{chr(10).join(f"{i+1}. {r}" for i, r in enumerate(state['analysis'].get('recommendations', [])))}
"""
    return {"report": report}
```

#### 5-3. 그래프 구성

```python
def create_analysis_workflow():
    """분석 워크플로우 생성"""
    workflow = StateGraph(AnalysisState)

    # 노드 추가
    workflow.add_node("parse", parse_logs_node)
    workflow.add_node("classify", classify_node)
    workflow.add_node("analyze", analyze_infrastructure_node)
    workflow.add_node("report", generate_report_node)

    # 엣지 연결
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "classify")
    workflow.add_edge("classify", "analyze")
    workflow.add_edge("analyze", "report")
    workflow.add_edge("report", END)

    # 컴파일
    app = workflow.compile()
    return app
```

### 테스트

```python
# tests/test_workflow.py
from src.graph.workflow import create_analysis_workflow

def test_full_workflow():
    app = create_analysis_workflow()

    result = app.invoke({
        "log_file_path": "datasets/scenario-01-db-connection-failure/dataset-01.log"
    })

    print(result['report'])
    assert 'report' in result

if __name__ == '__main__':
    test_full_workflow()
```

---

## Phase 6: Chainlit UI 구현 (1-2시간)

### 목표
웹 기반 사용자 인터페이스

### 파일: `src/ui/app.py`

### 구현 내용

```python
import chainlit as cl
from src.graph.workflow import create_analysis_workflow

# 워크플로우 생성
app = create_analysis_workflow()

@cl.on_chat_start
async def start():
    """채팅 시작"""
    await cl.Message(
        content="""# 🔍 로그 분석 시스템

로그 파일을 업로드하면 AI 에이전트가 분석합니다.

**지원 시나리오**:
- 🔴 데이터베이스 연결 장애
- 🟠 보안 공격 (XSS, Brute Force)
- 🟡 성능 문제 (N+1 쿼리, 메모리 누수)

파일을 업로드해주세요!"""
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """메시지 처리"""
    # 파일 확인
    if not message.elements:
        await cl.Message(content="❌ 로그 파일을 업로드해주세요!").send()
        return

    log_file = message.elements[0]

    # 진행 상황 메시지
    msg = cl.Message(content="")
    await msg.send()

    # 분석 실행
    await msg.stream_token("## 🔄 분석 중...\n\n")
    await msg.stream_token("✅ 1/4 로그 파싱 완료\n")

    result = app.invoke({"log_file_path": log_file.path})

    await msg.stream_token("✅ 2/4 문제 분류 완료\n")
    await msg.stream_token("✅ 3/4 상세 분석 완료\n")
    await msg.stream_token("✅ 4/4 보고서 생성 완료\n\n")
    await msg.update()

    # 보고서 표시
    await cl.Message(content=result['report']).send()
```

### 실행

```bash
chainlit run src/ui/app.py
```

---

## Phase 7: 추가 에이전트 확장 (선택사항)

### 7-1. 보안 분석 에이전트

**파일**: `src/agents/security_analyst.py`

**탐지 항목**:
- XSS 공격 패턴
- 무차별 대입 공격
- 권한 상승 시도

### 7-2. 성능 분석 에이전트

**파일**: `src/agents/performance_analyst.py`

**탐지 항목**:
- 느린 쿼리
- N+1 문제
- 메모리 누수

---

## 체크리스트

### 필수 구현 (MVP)
- [ ] 환경 설정 완료
- [ ] 로그 파서 구현
- [ ] 분류 에이전트 구현
- [ ] 인프라 분석 에이전트 구현
- [ ] LangGraph 워크플로우 구성
- [ ] Chainlit UI 구현
- [ ] 시나리오 1 테스트 성공

### 선택 구현
- [ ] 보안 분석 에이전트
- [ ] 성능 분석 에이전트
- [ ] 조건부 라우팅 구현
- [ ] 보고서 PDF 다운로드
- [ ] 다중 파일 업로드

---

## 디버깅 팁

### LLM 응답이 JSON이 아닐 때
```python
# response_format 사용
llm = ChatOpenAI(model="gpt-4", temperature=0.0)
response = llm.invoke(messages, response_format={"type": "json_object"})
```

### 토큰 제한 초과
```python
# 로그 샘플링
sampled_logs = parsed_logs[::10]  # 10개 중 1개만
```

### 에러 추적
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 다음 단계

1. ✅ 환경 설정부터 시작
2. 각 Phase를 순서대로 진행
3. 각 단계마다 테스트 실행
4. 문제 발생 시 디버깅 팁 참고

화이팅! 🚀