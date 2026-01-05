# Log Analysis Assistant (LangGraph + Chainlit) — Spec (Draft)

## 1) 목적 / 한 줄 정의
- **목적**: 실습용 가상 로그 스트림을 입력으로 받아, 이상/오류/보안 징후 및 관리자 변경 이력을 분석하고 **원인 추정 + 대응안 + 보고서**를 자동 생성한다.
- **한 줄 정의**: LangGraph 기반 멀티 에이전트가 로그를 정규화·탐지·상관분석·보고서화하고, Chainlit에서 대화형으로 결과를 조회/생성하는 로그 분석 어시스턴트.

## 2) 입력 / 출력
### 입력(실습 기준)
- 가상 생성 로그(지속 스트림 또는 배치): `INFO / WARN / ERROR / AUDIT(ADMIN)`
- 분석 조건: 시간 범위, 환경(prod/stage 가정), 서비스(optional), 필터(레벨/키워드/actor 등), 감사로그 포함 여부

### 출력
- **이슈 목록(Top N)**: 심각도, 발생량/영향, 근거 로그 샘플, 추정 원인(가설), 즉시 조치, 후속 과제
- **타임라인**: 이벤트 발생/급증 시점 + 관련 AUDIT 변경 연결
- **관리자 추적 리포트**: 누가/언제/무엇을 바꿨는지, 변경 이후 발생한 이상 징후 요약
- **보고서(Markdown)**: 공유 가능한 운영 보고서 포맷으로 생성

## 3) 관리자 기능 및 감사 로그(Audit) 범위
### 관리자 주요 기능(도메인)
- 공지사항(Notice): 작성/수정/삭제, Pin
- 카테고리(Category): 게시판 생성/삭제, 접근 권한 설정(adminOnly)
- 사용자(Member): 차단/해제, 권한 부여(승격)
- 게시물/댓글 관리: 강제 삭제, 신고 처리
- 이모티콘(Emoticon): 팩 등록/승인/삭제
- 시스템 설정: 서버 환경 설정 변경, 점검 모드

### 감사 로그 예시(요구)
- [ADMIN] Notice Created / Pinned / Deleted
- [ADMIN] Force Delete Post / Comment
- [ADMIN] User Banned / Unbanned / Role Changed / Password Reset Forced
- [ADMIN] Category Created / Permission Changed
- [ADMIN] Emoticon Pack Added
- [ADMIN] System Maintenance Mode Enabled (Duration 포함)

## 4) 전체 로그 레벨 시나리오(예시)
### INFO
- 사용자 활동(좋아요/채팅/알림/프로필 업데이트)

### WARN
- 로그인 실패 다발, rate limit 초과, sanitization 필터링(XSS 의심), slow query

### ERROR
- JWT 검증 실패, 디스크 부족, SMTP 타임아웃, DB 데드락

### AUDIT
- admin이 데이터/설정 변경(공지 pin, 카테고리 삭제, 시스템 설정 변경 등)

## 5) 핵심 기능(MVP)
- 로그 수집/정규화: 다양한 포맷을 공통 스키마로 변환
- 규칙 기반 탐지(MVP): 보안/신뢰성/관리자 감사 카테고리로 탐지
- 그룹핑/우선순위: 유사 오류 묶기 + 빈도/영향 기반 정렬
- 상관분석: AUDIT 변경 직후 발생한 WARN/ERROR 급증을 후보로 연결(점수화 + 근거)
- 대응안(런북) 제안: 즉시 조치 + 재발 방지 + 검증 단계
- 보고서 자동 작성: 요약/영향/타임라인/원인/조치/후속 과제
- QA/Critic: 과도한 단정 방지, 근거 부족 시 추가 데이터 요청 생성

## 6) 에이전트 구성(LangGraph)
### 오케스트레이션
- **Orchestrator/Router**: 사용자 요청 유형(장애 분석/보안/관리자 추적/보고서)을 분류하고 그래프 경로를 선택

### 파이프라인 에이전트(핵심)
- **Normalize Agent**: 파싱/정규화(공통 이벤트 스키마 생성)
- **Enrichment Agent**: actor/endpoint/리소스/요청 ID 등 태깅, 관련 이벤트 묶기

### 탐지 에이전트(병렬)
- **Security Detector**: failed login, JWT fail, rate limit, XSS 의심
- **Reliability Detector**: disk full, SMTP timeout, DB deadlock, slow query
- **Admin Audit Detector**: 관리자 변경 이벤트 구조화

### 분석/출력
- **Triage Agent**: 그룹핑 + 심각도/우선순위 산정 + 대표 증거 선택
- **Correlator Agent**: Audit 변경 ↔ 이상 징후 연결(시간창/대상/기능영역 기반)
- **Mitigation Agent**: 즉시조치/재발방지/검증 단계 제안
- **Report Writer Agent**: Markdown 보고서 생성
- **Critic Agent**: 결론의 근거/표현/누락 검토 및 보완 요구

### 기본 흐름(권장)
- Ingestion → Normalize → Enrich → (Detectors 병렬) → Triage → Correlate → Mitigation → Report → Critic

## 7) 사용자 시나리오(요약)
- 실시간 장애 감지: 최근 30분 분석 + Top 이슈/조치 + 감사 로그 상관
- 단일 오류 심층 분석: JWT invalid signature 원인 가설/검증 단계
- 보안 이벤트 대응: 공격 IP/대상 계정 그룹핑 + 대응 체크리스트
- 관리자 변경 추적: 카테고리 삭제/권한 변경 이후 영향 분석
- 정기 리포트: 일일/주간 운영 보고서 자동 생성
- 점검모드 운영: 점검 구간 전후 비교(예상 vs 비정상 오류 분리)

## 8) 추천 폴더 구조(초안)
> 실습용: 경계(생성/정규화/탐지/상관/보고/UX)를 명확히 분리

- apps/
  - chainlit_app/
    - main.py  (Chainlit entry)
- src/
  - config/            (settings)
  - domain/            (schemas/enums)
  - ingestion/         (log inputs)
  - normalization/     (parsers)
  - detection/         (security/reliability/admin)
  - correlation/       (audit ↔ events)
  - reporting/         (report renderer)
  - graph/             (LangGraph builder)
- prompts/
  - report/            (report templates)
  - triage/            (triage/summary prompts)
- data/
  - synthetic/         (raw synthetic logs)
  - normalized/        (normalized logs)
  - analysis/          (analysis outputs)
- scripts/
  - generate_logs.py
  - run_batch_analysis.py
- docs/
  - spec.md  (this file)

## 9) 데이터 저장 규칙(권장)
- 원본(가상) 로그: `data/synthetic/YYYY-MM-DD/*.jsonl`
- 정규화 로그: `data/normalized/YYYY-MM-DD/*.jsonl`
- 분석 결과: `data/analysis/{analysis_id}/`
  - `input_meta.json`
  - `findings.json`
  - `report.md`

## 10) 결정해야 할 사항(다음 단계)
- 로그 저장 포맷: **JSONL 권장**(스트리밍/배치 모두 유리)
- 스키마/검증: **Pydantic vs dataclass** 선택
- MVP 실행 방식: 1) 배치 분석 먼저(권장) → 2) 스트리밍/실시간 확장

## 11) 다음 설계 작업(코드 작성 전)
- `NormalizedEvent` / `Finding` / `AnalysisResult` 스키마 필드 확정
- 프롬프트/리포트 템플릿 파일 구조 확정(`prompts/**`)
- 규칙 기반 탐지 룰 목록화(심각도 기준 포함)
