"""Chainlit UI - 로그 분석 웹 인터페이스"""

import sys
from pathlib import Path
import chainlit as cl

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.graph.workflow import create_workflow
from src.graph.workflow import AnalysisState


@cl.on_chat_start
async def start():
    """채팅 시작 시 초기 메시지"""
    await cl.Message(
        content="""# 🔍 로그 분석 시스템

안녕하세요! 로그 파일을 업로드하면 AI가 자동으로 분석해드립니다.

## 📋 분석 가능한 항목
- **인프라 이슈**: DB 연결 장애, 서버 오류, 메모리 누수
- **보안 위협**: XSS 공격, SQL Injection, 무차별 대입 공격
- **성능 문제**: N+1 쿼리, 느린 응답, 리소스 병목

## 🚀 사용 방법
1. 로그 파일(.log)을 업로드해주세요
2. AI가 자동으로 분석을 시작합니다
3. 분석 결과와 권장 조치사항을 확인하세요

**파일을 업로드하려면 아래 클립 아이콘을 클릭하세요!** 📎
"""
    ).send()

    # 세션에 워크플로우 저장
    workflow = create_workflow()
    cl.user_session.set("workflow", workflow)


@cl.on_message
async def main(message: cl.Message):
    """메시지 수신 처리"""

    # 파일 업로드 확인
    if not message.elements:
        await cl.Message(
            content="⚠️ 로그 파일을 업로드해주세요. 아래 클립 아이콘(📎)을 클릭하세요."
        ).send()
        return

    # 업로드된 파일 처리
    file = message.elements[0]

    # .log 파일 확인
    if not file.name.endswith('.log'):
        await cl.Message(
            content=f"❌ '.log' 파일만 업로드 가능합니다. (업로드된 파일: {file.name})"
        ).send()
        return

    # 분석 시작 메시지
    start_msg = await cl.Message(
        content=f"## 📝 로그 분석 시작\n\n파일: `{file.name}`"
    ).send()

    try:
        # 워크플로우 가져오기
        workflow = cl.user_session.get("workflow")

        # Step 1: 로그 파싱
        step1_msg = cl.Message(content="### [1/4] 🔄 로그 파싱 중...")
        await step1_msg.send()

        from src.agents.log_parser import LogParserAgent
        parser = LogParserAgent()
        parser.parse_file(file.path)
        stats = parser.get_statistics()
        log_data = parser.format_for_llm()

        step1_msg.content = f"""### [1/4] ✅ 로그 파싱 완료

- 총 로그 라인: **{stats['total_lines']}**
- ERROR: **{stats['error_count']}**, WARN: **{stats['warn_count']}**, INFO: **{stats['info_count']}**
- 시간 범위: `{stats['time_range']['start']}` ~ `{stats['time_range']['end']}`
"""
        await step1_msg.update()

        # Step 2: 분류
        step2_msg = cl.Message(content="### [2/4] 🔄 카테고리 분류 중...")
        await step2_msg.send()

        from src.agents.classifier import ClassificationAgent
        classifier = ClassificationAgent()
        classification = classifier.classify(log_data)

        category_emoji = {
            'infrastructure': '🏗️',
            'security': '🔒',
            'performance': '⚡',
            'application': '💻',
            'user': '👤'
        }

        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }

        step2_msg.content = f"""### [2/4] ✅ 분류 완료

- 카테고리: {category_emoji.get(classification['category'], '📋')} **{classification['category'].upper()}**
- 심각도: {severity_emoji.get(classification['severity'], '⚪')} **{classification['severity'].upper()}**
- 신뢰도: **{classification['confidence']}**

**분류 이유:**
> {classification['reason']}
"""
        await step2_msg.update()

        # Step 3: 심층 분석
        step3_msg = cl.Message(content="### [3/4] 🔄 심층 분석 중...")
        await step3_msg.send()

        category = classification['category']
        analysis = None

        if category == 'infrastructure' or category == 'application':
            from src.agents.infrastructure_analyst import InfrastructureAnalystAgent
            analyst = InfrastructureAnalystAgent()
            analysis = analyst.analyze(log_data, classification)

        elif category == 'security':
            from src.agents.security_analyst import SecurityAnalystAgent
            analyst = SecurityAnalystAgent()
            analysis = analyst.analyze(log_data, classification)

        elif category == 'performance':
            from src.agents.performance_analyst import PerformanceAnalystAgent
            analyst = PerformanceAnalystAgent()
            analysis = analyst.analyze(log_data, classification)

        step3_msg.content = "### [3/4] ✅ 심층 분석 완료"
        await step3_msg.update()

        # Step 4: 최종 보고서
        await cl.Message(content="### [4/4] 📊 최종 보고서 생성 중...").send()

        # 보고서 생성
        report = generate_report(classification, analysis, stats)

        await cl.Message(content=report).send()

        # 완료 메시지
        await cl.Message(
            content="---\n\n✨ **분석이 완료되었습니다!** 추가 분석이 필요하면 다른 로그 파일을 업로드해주세요."
        ).send()

    except Exception as e:
        await cl.Message(
            content=f"❌ **분석 중 오류가 발생했습니다**\n\n```\n{str(e)}\n```"
        ).send()


def generate_report(classification: dict, analysis: dict, stats: dict) -> str:
    """최종 분석 보고서 생성"""

    category = classification['category']

    # 공통 헤더
    report = f"""# 📊 로그 분석 보고서

## 요약 (Executive Summary)

- **카테고리**: {classification['category'].upper()}
- **심각도**: {classification['severity'].upper()}
- **총 로그 라인**: {stats['total_lines']}
- **에러 발생**: {stats['error_count']}건

---

"""

    # 카테고리별 상세 분석
    if category in ['infrastructure', 'application']:
        report += f"""## 🏗️ 인프라 분석

### 🔍 이슈 유형
**{analysis['issue_type']}**

### 💡 근본 원인
{analysis['root_cause']}

### 📈 영향 분석
{analysis['impact_analysis']}

### ⚠️ 영향받는 컴포넌트
"""
        for component in analysis['affected_components']:
            report += f"- {component}\n"

        report += f"""
### 🔧 권장 조치사항

"""
        for i, action in enumerate(analysis['recommended_actions'], 1):
            report += f"{i}. {action}\n"

        report += f"""
### ⏰ 긴급도 및 복구 시간
- **긴급도**: {analysis['urgency'].upper()}
- **예상 복구 시간**: {analysis['estimated_recovery_time']}
"""

    elif category == 'security':
        report += f"""## 🔒 보안 분석

### 🎯 공격 유형
**{analysis['attack_type']}**

### 📋 공격 패턴
{analysis['attack_pattern']}

### 👤 공격자 정보
"""
        for key, value in analysis['attacker_info'].items():
            report += f"- **{key}**: {value}\n"

        report += f"""
### 🚨 보안 영향
{analysis['security_impact']}

### 🛡️ 취약점 평가
{analysis['vulnerability_assessment']}

### ⚡ 즉각 대응 조치

"""
        for i, action in enumerate(analysis['immediate_response'], 1):
            report += f"{i}. {action}\n"

        report += f"""
### 🔐 장기 보안 강화

"""
        for i, action in enumerate(analysis['recommended_actions'], 1):
            report += f"{i}. {action}\n"

    elif category == 'performance':
        report += f"""## ⚡ 성능 분석

### 🎯 성능 이슈
**{analysis['performance_issue']}**

### 🔍 병목 분석
{analysis['bottleneck_analysis']}

### 📊 성능 메트릭
"""
        for key, value in analysis['metrics'].items():
            report += f"- **{key}**: {value}\n"

        report += f"""
### 👥 사용자 영향
{analysis['impact_on_users']}

### 💡 근본 원인
{analysis['root_cause']}

### ⚡ Quick Wins (즉시 적용 가능)

"""
        for i, action in enumerate(analysis['quick_wins'], 1):
            report += f"{i}. {action}\n"

        report += f"""
### 🎯 장기 최적화 계획

"""
        for i, action in enumerate(analysis['optimization_plan'], 1):
            report += f"{i}. {action}\n"

        report += f"""
### 📈 예상 개선 효과
{analysis['estimated_improvement']}
"""

    report += "\n---\n\n🤖 *이 보고서는 AI에 의해 자동 생성되었습니다.*"

    return report