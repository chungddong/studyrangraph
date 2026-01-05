# Raw Synthetic Log Format (JSONL) — Draft

## 1) 목적
- 가상 로그 생성기와 샘플 데이터가 **동일한 입력 포맷**을 사용하도록 규약을 정의한다.
- 이 raw 로그는 `NormalizedEvent`로 변환(정규화)되기 전 단계이며, 파서/정규화기 입력으로 사용한다.

## 2) 파일 포맷
- 파일은 **JSONL**(JSON Lines)
  - 한 줄 = JSON object 1개
  - UTF-8 인코딩 권장
- 저장 위치 권장
  - `data/synthetic/YYYY-MM-DD/*.jsonl`

## 3) 최소 필드(Required)
> MVP 기준: 생성기가 반드시 넣어야 하는 최소 필드

- `ts`: string
  - ISO8601 권장 (예: `2026-01-05T14:55:00+09:00`)
- `level`: string
  - `INFO | WARN | ERROR | AUDIT`
- `msg`: string
  - 사람이 읽는 원문 메시지(보고서/디버깅 근거로 그대로 사용 가능)

## 4) 권장 필드(Optional)
> 필드가 있으면 정규화 품질/탐지 품질이 크게 올라감. 없으면 정규화 단계에서 `meta`로 흡수.

### 공통
- `service`: string (예: `community`)
- `env`: string (예: `local | dev | stage | prod`)
- `event_type`: string
  - 가능하면 생성 단계에서 지정(없으면 정규화기에서 msg 기반으로 추론)
- `actor`: object
  - `type`: `user|admin|system|unknown`
  - `id`: string
  - `ip`: string
- `target`: object
  - `type`: string (예: `post`, `comment`, `notice`, `category`, `system_config`, `table`)
  - `id`: string
  - `name`: string
- `http`: object
  - `method`: string
  - `path`: string
  - `query`: string
  - `status_code`: number
  - `client_ip`: string
- `trace_id`: string
- `request_id`: string
- `duration_ms`: number
- `meta`: object
  - 위에 없는 모든 확장 정보(키-값)

### ERROR 권장
- `error`: object
  - `code`: string
  - `message`: string
  - `stacktrace`: string

### DB 권장
- `db`: object
  - `table`: string
  - `duration_ms`: number
  - `query_fingerprint`: string

### AUDIT 권장
- `audit`: object
  - `entity`: string (예: `notice`, `category`, `system_config`)
  - `entity_id`: string
  - `action`: string (예: `created|updated|deleted|pinned`)
  - `changes`: array
    - item: `{ "field": string, "before": any, "after": any }`
  - `reason`: string
  - `duration_minutes`: number

## 5) JSONL 예시(시나리오 커버)

### INFO
```json
{"ts":"2026-01-05T14:00:00+09:00","level":"INFO","service":"community","env":"local","event_type":"POST_LIKED","actor":{"type":"user","id":"user_05"},"target":{"type":"post","id":"772"},"msg":"User [user_05] liked post [772]"}
{"ts":"2026-01-05T14:05:00+09:00","level":"INFO","service":"community","env":"local","event_type":"CHAT_MESSAGE_CREATED","actor":{"type":"user","id":"user_05"},"target":{"type":"chat_room","id":"room_abc"},"msg":"New chat message in room [room_abc] from [user_05]"}
{"ts":"2026-01-05T14:10:00+09:00","level":"INFO","service":"community","env":"local","event_type":"NOTIFICATION_DELIVERED","actor":{"type":"system"},"target":{"type":"notification","id":"COMMENT"},"meta":{"delivered_to":"user_10"},"msg":"Notification [type: COMMENT] delivered to user [user_10]"}
{"ts":"2026-01-05T14:15:00+09:00","level":"INFO","service":"community","env":"local","event_type":"PROFILE_IMAGE_UPDATED","actor":{"type":"user","id":"user_22"},"meta":{"url":"/uploads/profiles/..."},"msg":"Profile image updated for user [user_22] (URL: /uploads/profiles/...)"}
```

### WARN
```json
{"ts":"2026-01-05T14:20:00+09:00","level":"WARN","service":"community","env":"local","event_type":"AUTH_LOGIN_FAILED_BURST","actor":{"type":"unknown","id":"user_unknown","ip":"211.x.x.x"},"meta":{"attempt_count":5},"msg":"Multiple failed login attempts (5 times) for user [user_unknown] from IP [211.x.x.x]"}
{"ts":"2026-01-05T14:25:00+09:00","level":"WARN","service":"community","env":"local","event_type":"RATE_LIMIT_EXCEEDED","http":{"path":"/api/posts/search","client_ip":"182.x.x.x"},"msg":"Rate limit exceeded for API [/api/posts/search] by IP [182.x.x.x]"}
{"ts":"2026-01-05T14:30:00+09:00","level":"WARN","service":"community","env":"local","event_type":"INPUT_SANITIZED_XSS","actor":{"type":"user","id":"user_恶意"},"msg":"Sanitization filtered suspicious script tag from user [user_恶意]"}
{"ts":"2026-01-05T14:35:00+09:00","level":"WARN","service":"community","env":"local","event_type":"SLOW_QUERY","http":{"method":"GET","path":"/api/posts","query":"category=all&search=..."},"duration_ms":1500,"msg":"Slow query detected (1.5s): GET /api/posts?category=all&search=..."}
```

### ERROR
```json
{"ts":"2026-01-05T14:40:00+09:00","level":"ERROR","service":"community","env":"local","event_type":"AUTH_JWT_INVALID_SIGNATURE","error":{"code":"JWT_INVALID_SIGNATURE","message":"Invalid Signature"},"msg":"JWT Verification failed: Invalid Signature"}
{"ts":"2026-01-05T14:45:00+09:00","level":"ERROR","service":"community","env":"local","event_type":"STORAGE_NO_SPACE_LEFT","storage":{"error":"No space left on device"},"msg":"File Upload failed: No space left on device"}
{"ts":"2026-01-05T14:50:00+09:00","level":"ERROR","service":"community","env":"local","event_type":"MAIL_SMTP_TIMEOUT","mail":{"recipient":"user_email"},"error":{"code":"SMTP_TIMEOUT"},"msg":"Mail sending failed to [user_email] (SMTP Timeout)"}
{"ts":"2026-01-05T14:55:00+09:00","level":"ERROR","service":"community","env":"local","event_type":"DB_DEADLOCK","db":{"table":"PostLike"},"error":{"code":"DB_DEADLOCK"},"msg":"Database Deadlock detected on Table [PostLike]"}
```

### AUDIT
```json
{"ts":"2026-01-05T15:00:00+09:00","level":"AUDIT","service":"community","env":"local","event_type":"AUDIT_ENTITY_CHANGED","actor":{"type":"admin","id":"admin_01"},"audit":{"entity":"notice","entity_id":"5","action":"updated","changes":[{"field":"isPinned","before":false,"after":true}]},"msg":"[admin_01] changed 'notice' table entry [id:5] - isPinned: false -> true"}
{"ts":"2026-01-05T15:05:00+09:00","level":"AUDIT","service":"community","env":"local","event_type":"AUDIT_ENTITY_DELETED","actor":{"type":"admin","id":"admin_02"},"target":{"type":"category","id":"12","name":"OldBoard"},"audit":{"entity":"category","entity_id":"12","action":"deleted"},"msg":"[admin_02] deleted category [id:12, name:'OldBoard']"}
{"ts":"2026-01-05T15:10:00+09:00","level":"AUDIT","service":"community","env":"local","event_type":"AUDIT_CONFIG_UPDATED","actor":{"type":"admin","id":"super_admin"},"target":{"type":"system_config","id":"MAX_POSTS_PER_DAY"},"audit":{"entity":"system_config","entity_id":"MAX_POSTS_PER_DAY","action":"updated","changes":[{"field":"MAX_POSTS_PER_DAY","before":10,"after":50}]},"msg":"[super_admin] updated system config: 'MAX_POSTS_PER_DAY' from 10 to 50"}
```

## 6) 정규화(Normalize) 규칙(요약)
- raw 로그에서 `event_type`가 없으면 `msg` 패턴 기반으로 추론
- raw의 `actor/http/target/audit/error/db/...`는 존재하면 그대로 옮기고,
  없는 정보는 `meta`로 흡수하거나 `None`으로 둔다.
- raw JSON 전체는 `NormalizedEvent.raw`로 보관한다.
