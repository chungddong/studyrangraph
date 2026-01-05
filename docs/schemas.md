# Schemas — Draft (Pydantic-oriented)

## 1) 목적
- 다양한 원본 로그 포맷을 내부 공통 표현인 **NormalizedEvent**로 통일한다.
- 탐지/상관/보고서 산출물은 **Finding / AnalysisResult**에만 의존하도록 데이터 계약(contract)을 고정한다.

## 2) 공통 규칙
- 시간은 ISO8601 권장: `2026-01-05T14:55:00+09:00` (또는 timezone 없는 `Z`)
- `event_id`는 UUID 문자열 권장(분석/보고서에서 근거 참조에 사용)
- `raw`에는 원본 한 줄(문자열 또는 dict)을 저장(재현/디버깅용)
- 확장 필드는 `meta`(dict)로 흡수하여 MVP 단계에서 스키마 경직을 방지

## 3) Enum 후보
- `LogLevel`: `INFO | WARN | ERROR | AUDIT`
- `EventCategory`: `activity | security | reliability | performance | admin_audit`
- `Severity`: `low | medium | high | critical`
- `ActorType`: `user | admin | system | unknown`

## 4) event_type 후보(현재 시나리오 100% 커버)
### Activity(INFO)
- `POST_LIKED`
- `CHAT_MESSAGE_CREATED`
- `NOTIFICATION_DELIVERED`
- `PROFILE_IMAGE_UPDATED`

### Security/Warn/Error
- `AUTH_LOGIN_FAILED_BURST` (failed login N회)
- `RATE_LIMIT_EXCEEDED`
- `INPUT_SANITIZED_XSS`
- `AUTH_JWT_INVALID_SIGNATURE`

### Performance/Warn
- `SLOW_QUERY`

### Reliability/Error
- `STORAGE_NO_SPACE_LEFT`
- `MAIL_SMTP_TIMEOUT`
- `DB_DEADLOCK`

### Admin/Audit
- `ADMIN_NOTICE_CREATED`
- `ADMIN_NOTICE_PINNED`
- `ADMIN_NOTICE_DELETED`
- `ADMIN_FORCE_DELETE_POST`
- `ADMIN_FORCE_DELETE_COMMENT`
- `ADMIN_USER_BANNED`
- `ADMIN_USER_UNBANNED`
- `ADMIN_ROLE_CHANGED`
- `ADMIN_PASSWORD_RESET_FORCED`
- `ADMIN_CATEGORY_CREATED`
- `ADMIN_CATEGORY_PERMISSION_CHANGED`
- `ADMIN_EMOTICON_PACK_ADDED`
- `ADMIN_MAINTENANCE_MODE_ENABLED`
- `AUDIT_ENTITY_CHANGED`
- `AUDIT_ENTITY_DELETED`
- `AUDIT_CONFIG_UPDATED`

---

## 5) NormalizedEvent(정규화 이벤트) 필드
> 아래 타입 표기는 “권장 타입”이며, 구현에서는 Pydantic 모델로 선언.

### Sub-model: Actor
- `type`: ActorType
- `id`: str | None  (예: `user_05`, `admin_01`, `super_admin`)
- `ip`: str | None

### Sub-model: Target
- `type`: str | None  (예: `post`, `comment`, `notice`, `category`, `system_config`, `table`)
- `id`: str | None    (예: `772`, `PostLike`, `MAX_POSTS_PER_DAY`)
- `name`: str | None  (예: `SecretBoard`, `Winter_Special_2026`)

### Sub-model: HttpContext (선택)
- `method`: str | None
- `path`: str | None
- `query`: str | None
- `status_code`: int | None
- `client_ip`: str | None

### Sub-model: AuditChange (선택)
- `field`: str
- `before`: str | int | float | bool | None
- `after`: str | int | float | bool | None

### Sub-model: AuditContext (선택)
- `entity`: str | None            (예: `notice`, `category`, `system_config`)
- `entity_id`: str | None         (예: `5`, `12`)
- `action`: str | None            (예: `created`, `pinned`, `deleted`, `updated`)
- `changes`: list[AuditChange]    (필드 변경 내역)
- `reason`: str | None
- `duration_minutes`: int | None

### Sub-model: ErrorContext (선택)
- `code`: str | None              (예: `JWT_INVALID_SIGNATURE`, `SMTP_TIMEOUT`)
- `message`: str | None
- `stacktrace`: str | None

### Sub-model: DbContext (선택)
- `table`: str | None             (예: `PostLike`)
- `query_fingerprint`: str | None
- `duration_ms`: int | None

### Sub-model: AuthContext (선택)
- `subject_user`: str | None      (대상 사용자)
- `attempt_count`: int | None     (실패 횟수)
- `token_type`: str | None        (예: `access`)
- `failure_reason`: str | None    (예: `Invalid Signature`)

### Sub-model: RateLimitContext (선택)
- `key`: str | None               (예: IP or user)
- `limit`: int | None
- `window_sec`: int | None

### Sub-model: MailContext (선택)
- `recipient`: str | None
- `provider`: str | None

### Sub-model: StorageContext (선택)
- `path`: str | None
- `error`: str | None             (예: `No space left on device`)

### NormalizedEvent (본체)
- `event_id`: str
- `timestamp`: str (또는 datetime)
- `level`: LogLevel
- `category`: EventCategory
- `event_type`: str
- `message`: str
- `service`: str | None
- `environment`: str | None

- `actor`: Actor | None
- `target`: Target | None
- `http`: HttpContext | None

- `duration_ms`: int | None
- `error`: ErrorContext | None
- `db`: DbContext | None
- `auth`: AuthContext | None
- `rate_limit`: RateLimitContext | None
- `mail`: MailContext | None
- `storage`: StorageContext | None
- `audit`: AuditContext | None

- `trace_id`: str | None
- `request_id`: str | None

- `meta`: dict[str, object]  (추가 필드 수용)
- `raw`: object | None       (원본 라인 저장)

---

## 6) 분석 산출물 스키마(탐지/상관/보고서)

### Sub-model: Evidence
- `event_id`: str
- `timestamp`: str
- `excerpt`: str              (원문 일부)

### Sub-model: Hypothesis
- `title`: str
- `confidence`: str           (예: `high|medium|low`)
- `rationale`: str            (근거 요약)
- `next_checks`: list[str]    (추가로 확인할 로그/조건)

### Sub-model: RecommendedAction
- `title`: str
- `type`: str                 (예: `mitigation|prevention|verification`)
- `steps`: list[str]

### Sub-model: Correlation
- `audit_event_id`: str
- `finding_id`: str
- `score`: float              (0~1 권장)
- `rationale`: str

### Finding
- `finding_id`: str
- `category`: EventCategory
- `severity`: Severity
- `title`: str
- `summary`: str
- `first_seen`: str | None
- `last_seen`: str | None
- `count`: int | None
- `affected_endpoints`: list[str]
- `affected_actors`: list[str]
- `evidence`: list[Evidence]
- `hypotheses`: list[Hypothesis]
- `recommended_actions`: list[RecommendedAction]
- `related_audit_event_ids`: list[str]

### AnalysisResult
- `analysis_id`: str
- `time_range`: object         (예: `{start, end}`)
- `filters`: object            (예: `{level, service, include_audit}`)
- `findings`: list[Finding]
- `correlations`: list[Correlation]
- `report_markdown`: str | None

---

## 7) 예시 로그 → NormalizedEvent 매핑(요약)

### INFO
- `User [user_05] liked post [772]`
  - `level=INFO`, `category=activity`, `event_type=POST_LIKED`
  - `actor={type:user, id:user_05}` / `target={type:post, id:772}`

- `New chat message in room [room_abc] from [user_05]`
  - `event_type=CHAT_MESSAGE_CREATED`, `target={type:chat_room, id:room_abc}`

- `Notification [type: COMMENT] delivered to user [user_10]`
  - `event_type=NOTIFICATION_DELIVERED`, `target={type:notification, id:COMMENT}`
  - `meta={delivered_to:user_10}`

- `Profile image updated for user [user_22] (URL: ...)`
  - `event_type=PROFILE_IMAGE_UPDATED`, `actor={type:user, id:user_22}`
  - `meta={url:"/uploads/profiles/..."}`

### WARN
- `Multiple failed login attempts (5 times) for user [user_unknown] from IP [211.x.x.x]`
  - `category=security`, `event_type=AUTH_LOGIN_FAILED_BURST`
  - `actor={type:unknown, id:user_unknown, ip:211.x.x.x}`
  - `auth={subject_user:user_unknown, attempt_count:5}`

- `Rate limit exceeded for API [/api/posts/search] by IP [182.x.x.x]`
  - `category=security`, `event_type=RATE_LIMIT_EXCEEDED`
  - `http={path:"/api/posts/search", client_ip:"182.x.x.x"}`
  - `rate_limit={key:"182.x.x.x"}`

- `Sanitization filtered suspicious script tag from user [user_恶意]`
  - `category=security`, `event_type=INPUT_SANITIZED_XSS`
  - `actor={type:user, id:user_恶意}`

- `Slow query detected (1.5s): GET /api/posts?category=all&search=...`
  - `category=performance`, `event_type=SLOW_QUERY`
  - `http={method:GET, path:"/api/posts", query:"category=all&search=..."}`
  - `duration_ms=1500`

### ERROR
- `JWT Verification failed: Invalid Signature`
  - `category=security`, `event_type=AUTH_JWT_INVALID_SIGNATURE`
  - `auth={failure_reason:"Invalid Signature"}`
  - `error={code:"JWT_INVALID_SIGNATURE"}`

- `File Upload failed: No space left on device`
  - `category=reliability`, `event_type=STORAGE_NO_SPACE_LEFT`
  - `storage={error:"No space left on device"}`

- `Mail sending failed to [user_email] (SMTP Timeout)`
  - `category=reliability`, `event_type=MAIL_SMTP_TIMEOUT`
  - `mail={recipient:"user_email"}`
  - `error={code:"SMTP_TIMEOUT"}`

- `Database Deadlock detected on Table [PostLike]`
  - `category=reliability`, `event_type=DB_DEADLOCK`
  - `db={table:"PostLike"}`
  - `error={code:"DB_DEADLOCK"}`

### AUDIT / ADMIN
- `AUDIT: [admin_01] changed 'notice' table entry [id:5] - isPinned: false -> true`
  - `level=AUDIT`, `category=admin_audit`, `event_type=AUDIT_ENTITY_CHANGED`
  - `actor={type:admin, id:admin_01}`
  - `audit={entity:"notice", entity_id:"5", action:"updated", changes:[{field:"isPinned", before:false, after:true}]}`

- `AUDIT: [admin_02] deleted category [id:12, name:'OldBoard']`
  - `event_type=AUDIT_ENTITY_DELETED`
  - `actor={type:admin, id:admin_02}`
  - `audit={entity:"category", entity_id:"12", action:"deleted"}` + `target={type:category, id:12, name:OldBoard}`

- `AUDIT: [super_admin] updated system config: 'MAX_POSTS_PER_DAY' from 10 to 50`
  - `event_type=AUDIT_CONFIG_UPDATED`
  - `actor={type:admin, id:super_admin}`
  - `audit={entity:"system_config", entity_id:"MAX_POSTS_PER_DAY", action:"updated", changes:[{field:"MAX_POSTS_PER_DAY", before:10, after:50}]}`
