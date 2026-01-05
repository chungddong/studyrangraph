# 로그 분석 시나리오 문서

## 개요

MNU OUTSIDE API 서버에서 발생할 수 있는 다양한 이슈 상황을 시나리오로 구성하여, 다중 에이전트 시스템이 이를 분석하고 보고서를 생성할 수 있도록 합니다.

---

## 시나리오 분류 체계

### 심각도 레벨
- **🔴 Critical**: 시스템 전체에 영향을 미치는 심각한 문제
- **🟠 High**: 주요 기능 장애, 즉시 조치 필요
- **🟡 Medium**: 부분적 기능 저하, 모니터링 필요
- **🟢 Low**: 경미한 이슈, 정기 점검 시 해결

### 이슈 카테고리
1. **인프라** - 데이터베이스, 네트워크, 서버
2. **보안** - 인증, 권한, XSS, SQL Injection
3. **성능** - 응답 시간, N+1 쿼리, 메모리
4. **애플리케이션** - 비즈니스 로직 오류
5. **사용자** - 잘못된 입력, 비정상적인 행동 패턴

---

## 시나리오 목록

### 시나리오 1: 데이터베이스 연결 장애 🔴 Critical

**상황 설명**:
새벽 3시, 데이터베이스 서버가 갑자기 응답하지 않아 모든 API 요청이 실패하기 시작했습니다.

**발생 원인**:
- MariaDB 서비스 중단
- 네트워크 단절
- DB 서버 리소스 고갈

**로그 패턴**:
```
[2026-01-05 03:15:22] ERROR Database connection error: Error: connect ECONNREFUSED 127.0.0.1:3306
[2026-01-05 03:15:22] WARN Database connection failed, starting server without database
[2026-01-05 03:15:23] INFO Note: Registration and database-dependent features will not work
[2026-01-05 03:15:25] ERROR POST /register 500 - 12ms
[2026-01-05 03:15:26] ERROR GET /api/posts 500 - 8ms
[2026-01-05 03:15:28] ERROR POST /login 500 - 10ms
[2026-01-05 03:15:30] ERROR GET /api/profile 500 - 7ms
[2026-01-05 03:15:35] ERROR Database connection error: Error: connect ECONNREFUSED 127.0.0.1:3306
```

**예상 영향**:
- 모든 데이터베이스 의존 기능 중단
- 회원가입, 로그인 불가
- 게시글 조회/작성 불가
- 100% 서비스 장애

**에이전트가 감지해야 할 항목**:
1. 연속적인 `ECONNREFUSED` 에러
2. 모든 API 엔드포인트에서 500 에러 발생
3. 데이터베이스 관련 경고 메시지
4. 에러 발생 시간 패턴 (갑작스러운 발생)

**권장 조치**:
1. 즉시 DB 서버 상태 확인
2. DB 서비스 재시작
3. 네트워크 연결 상태 점검
4. 환경 변수 설정 확인

---

### 시나리오 2: XSS 공격 시도 🟠 High

**상황 설명**:
악의적인 사용자가 게시글 작성 시 스크립트 태그를 삽입하여 XSS 공격을 시도했습니다.

**발생 원인**:
- 악의적인 공격 시도
- 보안 테스트 수행
- 자동화된 봇 공격

**로그 패턴**:
```
[2026-01-05 14:32:15] INFO POST /api/posts - User: hacker123
[2026-01-05 14:32:15] WARN Dangerous HTML content detected: <script>alert('XSS')</script>
[2026-01-05 14:32:15] ERROR POST /api/posts 400 - 23ms - 허용되지 않는 HTML 태그나 스크립트가 포함되어 있습니다
[2026-01-05 14:32:18] INFO POST /api/posts - User: hacker123
[2026-01-05 14:32:18] WARN Dangerous HTML content detected: <img src=x onerror=alert(1)>
[2026-01-05 14:32:18] ERROR POST /api/posts 400 - 19ms - 허용되지 않는 HTML 태그나 스크립트가 포함되어 있습니다
[2026-01-05 14:32:22] INFO POST /api/posts - User: hacker123
[2026-01-05 14:32:22] WARN Dangerous HTML content detected: javascript:void(0)
[2026-01-05 14:32:22] ERROR POST /api/posts 400 - 21ms - 허용되지 않는 HTML 태그나 스크립트가 포함되어 있습니다
[2026-01-05 14:32:25] INFO POST /api/comments - User: hacker123
[2026-01-05 14:32:25] WARN Dangerous HTML content detected: <svg onload=alert(1)>
[2026-01-05 14:32:25] ERROR POST /api/comments 400 - 18ms - 허용되지 않는 HTML 태그나 스크립트가 포함되어 있습니다
```

**예상 영향**:
- 현재는 htmlSanitizer가 차단 중 ✅
- 차단 실패 시 사용자 세션 탈취 가능
- 다른 사용자에게 악성 스크립트 전파 가능

**에이전트가 감지해야 할 항목**:
1. 동일 사용자의 반복적인 공격 시도
2. 다양한 XSS 페이로드 패턴
3. 짧은 시간 내 여러 엔드포인트 공격
4. 보안 필터가 정상 동작 중임을 확인

**권장 조치**:
1. 해당 사용자 계정 일시 정지
2. IP 주소 차단 고려
3. 보안 로그 상세 분석
4. 다른 엔드포인트의 보안 점검

---

### 시나리오 3: N+1 쿼리 성능 문제 🟡 Medium

**상황 설명**:
게시글 목록 조회 시 각 게시글마다 댓글을 개별 조회하여 응답 시간이 급격히 증가했습니다.

**발생 원인**:
- relations 설정 누락
- 비효율적인 쿼리 구조
- 데이터 증가로 인한 성능 저하

**로그 패턴**:
```
[2026-01-05 11:20:15] INFO GET /api/posts?page=1&limit=20 - 1234ms
[2026-01-05 11:20:15] DEBUG Executed query: SELECT * FROM post LIMIT 20
[2026-01-05 11:20:15] DEBUG Executed query: SELECT * FROM comment WHERE postId = 1
[2026-01-05 11:20:15] DEBUG Executed query: SELECT * FROM comment WHERE postId = 2
[2026-01-05 11:20:15] DEBUG Executed query: SELECT * FROM comment WHERE postId = 3
[2026-01-05 11:20:15] DEBUG Executed query: SELECT * FROM comment WHERE postId = 4
... (20번 반복)
[2026-01-05 11:20:15] WARN Slow query detected: GET /api/posts - 1234ms (threshold: 200ms)
[2026-01-05 11:20:18] INFO GET /api/posts?page=1&limit=20 - 1198ms
[2026-01-05 11:20:22] INFO GET /api/posts?page=2&limit=20 - 1267ms
[2026-01-05 11:20:25] INFO GET /api/posts?page=1&limit=50 - 2845ms
[2026-01-05 11:20:25] WARN Slow query detected: GET /api/posts - 2845ms (threshold: 200ms)
```

**예상 영향**:
- 사용자 경험 저하 (느린 페이지 로딩)
- 서버 리소스 낭비
- 데이터베이스 부하 증가
- 동시 사용자 증가 시 심각한 성능 문제 발생 가능

**에이전트가 감지해야 할 항목**:
1. 반복적인 느린 쿼리 경고
2. 동일 엔드포인트의 일관된 성능 저하
3. 쿼리 실행 횟수 급증
4. 응답 시간이 임계값(200ms) 초과

**권장 조치**:
1. TypeORM relations 설정 추가
2. JOIN 쿼리 사용
3. 쿼리 최적화
4. 데이터베이스 인덱스 검토

---

### 시나리오 4: 무차별 대입 공격 (Brute Force) 🟠 High

**상황 설명**:
동일 IP에서 여러 계정에 대해 짧은 시간 내 반복적인 로그인 시도가 발생했습니다.

**발생 원인**:
- 자동화된 비밀번호 크래킹 시도
- 봇을 통한 무차별 공격
- 계정 탈취 시도

**로그 패턴**:
```
[2026-01-05 09:15:10] INFO POST /login - IP: 192.168.1.100 - user1@example.com
[2026-01-05 09:15:10] ERROR POST /login 401 - 125ms - 아이디와 비밀번호를 확인해주세요
[2026-01-05 09:15:11] INFO POST /login - IP: 192.168.1.100 - user1@example.com
[2026-01-05 09:15:11] ERROR POST /login 401 - 118ms - 아이디와 비밀번호를 확인해주세요
[2026-01-05 09:15:12] INFO POST /login - IP: 192.168.1.100 - user1@example.com
[2026-01-05 09:15:12] ERROR POST /login 401 - 122ms - 아이디와 비밀번호를 확인해주세요
[2026-01-05 09:15:13] INFO POST /login - IP: 192.168.1.100 - admin@example.com
[2026-01-05 09:15:13] ERROR POST /login 401 - 115ms - 아이디와 비밀번호를 확인해주세요
[2026-01-05 09:15:14] INFO POST /login - IP: 192.168.1.100 - admin@example.com
[2026-01-05 09:15:14] ERROR POST /login 401 - 120ms - 아이디와 비밀번호를 확인해주세요
[2026-01-05 09:15:15] INFO POST /login - IP: 192.168.1.100 - test@example.com
[2026-01-05 09:15:15] ERROR POST /login 401 - 119ms - 아이디와 비밀번호를 확인해주세요
... (계속 반복)
[2026-01-05 09:15:45] WARN Suspicious activity detected: 45 failed login attempts from IP 192.168.1.100 in 35 seconds
```

**예상 영향**:
- 계정 탈취 위험
- 서버 리소스 낭비
- 정상 사용자의 로그인 지연
- 데이터베이스 부하

**에이전트가 감지해야 할 항목**:
1. 동일 IP의 반복적인 로그인 실패
2. 짧은 시간 내 대량 요청
3. 여러 계정에 대한 시도
4. 일정 패턴의 요청 간격

**권장 조치**:
1. 즉시 해당 IP 차단
2. Rate limiting 적용
3. CAPTCHA 도입 검토
4. 계정 잠금 정책 적용
5. 보안 팀에 알림

---

### 시나리오 5: JWT 토큰 만료 급증 🟡 Medium

**상황 설명**:
특정 시간대에 많은 사용자의 JWT 토큰이 만료되어 인증 실패가 급증했습니다.

**발생 원인**:
- 토큰 갱신 로직 부재
- 짧은 토큰 만료 시간 설정
- 대규모 사용자 동시 로그인 이벤트 후

**로그 패턴**:
```
[2026-01-05 16:00:05] INFO GET /api/posts - User: user123
[2026-01-05 16:00:05] ERROR GET /api/posts 401 - 8ms - 유효하지 않은 토큰입니다
[2026-01-05 16:00:06] INFO GET /api/profile - User: user456
[2026-01-05 16:00:06] ERROR GET /api/profile 401 - 7ms - 유효하지 않은 토큰입니다
[2026-01-05 16:00:07] INFO POST /api/posts - User: user789
[2026-01-05 16:00:07] ERROR POST /api/posts 401 - 9ms - 유효하지 않은 토큰입니다
[2026-01-05 16:00:08] INFO GET /api/notifications - User: user321
[2026-01-05 16:00:08] ERROR GET /api/notifications 401 - 6ms - 유효하지 않은 토큰입니다
[2026-01-05 16:00:10] INFO GET /api/chat/rooms - User: user654
[2026-01-05 16:00:10] ERROR GET /api/chat/rooms 401 - 8ms - 유효하지 않은 토큰입니다
... (계속 증가)
[2026-01-05 16:01:00] WARN High rate of 401 errors detected: 156 token validation failures in last minute
[2026-01-05 16:01:15] INFO POST /login - user123 - Re-login after token expiry
[2026-01-05 16:01:16] INFO POST /login - user456 - Re-login after token expiry
```

**예상 영향**:
- 사용자 경험 저하 (갑작스러운 로그아웃)
- 재로그인으로 인한 사용자 불편
- 로그인 엔드포인트 트래픽 급증
- 고객 문의 증가

**에이전트가 감지해야 할 항목**:
1. 특정 시간대 401 에러 급증
2. 다양한 사용자의 토큰 만료
3. 재로그인 패턴 증가
4. 여러 엔드포인트에서 동시 발생

**권장 조치**:
1. JWT 토큰 만료 시간 연장 검토
2. Refresh Token 메커니즘 도입
3. 자동 토큰 갱신 로직 구현
4. 사용자에게 만료 전 알림

---

### 시나리오 6: 권한 상승 시도 🔴 Critical

**상황 설명**:
일반 사용자가 관리자 전용 API에 반복적으로 접근을 시도했습니다.

**발생 원인**:
- 권한 탈취 시도
- API 구조 탐색
- 보안 취약점 탐지 시도

**로그 패턴**:
```
[2026-01-05 13:45:20] INFO GET /api/categories - User: normaluser (role: user)
[2026-01-05 13:45:20] ERROR GET /api/categories 403 - 12ms - 관리자 권한이 필요합니다
[2026-01-05 13:45:22] INFO POST /api/categories - User: normaluser (role: user)
[2026-01-05 13:45:22] ERROR POST /api/categories 403 - 10ms - 관리자 권한이 필요합니다
[2026-01-05 13:45:25] INFO DELETE /api/posts/15 - User: normaluser (role: user)
[2026-01-05 13:45:25] ERROR DELETE /api/posts/15 403 - 15ms - 본인의 게시글만 삭제할 수 있습니다
[2026-01-05 13:45:28] INFO PUT /api/posts/23 - User: normaluser (role: user)
[2026-01-05 13:45:28] ERROR PUT /api/posts/23 403 - 14ms - 본인의 게시글만 수정할 수 있습니다
[2026-01-05 13:45:32] INFO POST /api/notices - User: normaluser (role: user)
[2026-01-05 13:45:32] ERROR POST /api/notices 403 - 11ms - 관리자 권한이 필요합니다
[2026-01-05 13:45:35] WARN Privilege escalation attempt detected: User normaluser attempted 5 unauthorized actions
```

**예상 영향**:
- 시스템 보안 위협
- 데이터 무결성 위험
- 권한 시스템 우회 가능성
- 다른 사용자 데이터 접근 시도

**에이전트가 감지해야 할 항목**:
1. 동일 사용자의 반복적인 403 에러
2. 관리자 전용 엔드포인트 접근 시도
3. 타인 소유 리소스 수정/삭제 시도
4. 짧은 시간 내 여러 권한 위반

**권장 조치**:
1. 즉시 해당 계정 정지
2. 보안 로그 상세 분석
3. 권한 검증 로직 점검
4. IP 주소 추적 및 차단
5. 보안 팀 긴급 알림

---

### 시나리오 7: 메모리 누수로 인한 서버 성능 저하 🟠 High

**상황 설명**:
시간이 지남에 따라 서버 응답 시간이 점진적으로 증가하고 메모리 사용량이 계속 늘어났습니다.

**발생 원인**:
- 메모리 해제 실패
- 이벤트 리스너 미정리
- 캐시 무한 증가
- DB 커넥션 미반환

**로그 패턴**:
```
[2026-01-05 08:00:00] INFO Server memory usage: 256MB
[2026-01-05 08:00:00] INFO GET /api/posts 200 - 45ms
[2026-01-05 09:00:00] INFO Server memory usage: 384MB
[2026-01-05 09:00:00] INFO GET /api/posts 200 - 67ms
[2026-01-05 10:00:00] INFO Server memory usage: 512MB
[2026-01-05 10:00:00] INFO GET /api/posts 200 - 89ms
[2026-01-05 11:00:00] INFO Server memory usage: 768MB
[2026-01-05 11:00:00] WARN High memory usage detected: 768MB (threshold: 512MB)
[2026-01-05 11:00:00] INFO GET /api/posts 200 - 134ms
[2026-01-05 12:00:00] INFO Server memory usage: 1024MB
[2026-01-05 12:00:00] ERROR Server memory usage: 1024MB (critical threshold: 1024MB)
[2026-01-05 12:00:00] WARN Slow query detected: GET /api/posts - 256ms
[2026-01-05 12:30:00] INFO Server memory usage: 1280MB
[2026-01-05 12:30:00] ERROR Memory leak suspected - continuous memory growth detected
[2026-01-05 12:30:15] WARN GET /api/posts 200 - 412ms
[2026-01-05 12:30:30] ERROR GET /api/chat/rooms 500 - 2145ms - Out of memory
```

**예상 영향**:
- 점진적인 성능 저하
- 서버 크래시 위험
- 모든 사용자의 서비스 이용 지연
- 최종적으로 서비스 중단

**에이전트가 감지해야 할 항목**:
1. 지속적인 메모리 증가 추세
2. 응답 시간 점진적 증가
3. 메모리 임계값 초과
4. 시간대별 성능 저하 패턴

**권장 조치**:
1. 즉시 서버 재시작
2. 메모리 프로파일링 수행
3. 이벤트 리스너 정리 로직 점검
4. DB 커넥션 풀 설정 확인
5. 캐시 전략 재검토

---

### 시나리오 8: 입력 검증 실패로 인한 대량 400 에러 🟢 Low

**상황 설명**:
새로운 클라이언트 배포 후 필수 필드 누락으로 인한 400 에러가 급증했습니다.

**발생 원인**:
- 프론트엔드 배포 오류
- API 스펙 불일치
- 클라이언트 버그

**로그 패턴**:
```
[2026-01-05 15:30:10] INFO POST /api/posts - User: user123
[2026-01-05 15:30:10] ERROR POST /api/posts 400 - 15ms - 제목은 필수입니다
[2026-01-05 15:30:15] INFO POST /api/posts - User: user456
[2026-01-05 15:30:15] ERROR POST /api/posts 400 - 12ms - 제목은 필수입니다
[2026-01-05 15:30:18] INFO POST /api/comments - User: user789
[2026-01-05 15:30:18] ERROR POST /api/comments 400 - 10ms - 댓글 내용은 필수입니다
[2026-01-05 15:30:22] INFO POST /api/posts - User: user321
[2026-01-05 15:30:22] ERROR POST /api/posts 400 - 14ms - 카테고리는 필수입니다
[2026-01-05 15:30:25] INFO POST /api/posts - User: user654
[2026-01-05 15:30:25] ERROR POST /api/posts 400 - 13ms - 제목은 필수입니다
... (계속 반복)
[2026-01-05 15:35:00] WARN High rate of 400 errors: 125 validation failures in last 5 minutes
[2026-01-05 15:35:00] INFO Error pattern: "제목은 필수입니다" - 89 occurrences
```

**예상 영향**:
- 사용자가 게시글/댓글 작성 실패
- 사용자 불만 증가
- 고객 문의 급증
- 서비스 신뢰도 저하

**에이전트가 감지해야 할 항목**:
1. 특정 시간 이후 400 에러 급증
2. 동일한 에러 메시지 반복
3. 특정 엔드포인트 집중 발생
4. 배포 시간과의 상관관계

**권장 조치**:
1. 프론트엔드 배포 롤백 검토
2. API 스펙 문서 확인
3. 개발팀에 긴급 알림
4. 클라이언트 버그 수정 및 핫픽스 배포

---

## 시나리오 요약 테이블

| 시나리오 | 심각도 | 카테고리 | 주요 지표 | 예상 조치 시간 |
|---------|--------|---------|----------|--------------|
| 1. DB 연결 장애 | 🔴 Critical | 인프라 | ECONNREFUSED, 500 에러 | 즉시 (0-15분) |
| 2. XSS 공격 시도 | 🟠 High | 보안 | 악성 스크립트 감지, 400 에러 | 긴급 (15-60분) |
| 3. N+1 쿼리 문제 | 🟡 Medium | 성능 | 느린 응답, 쿼리 증가 | 우선 (1-4시간) |
| 4. 무차별 대입 공격 | 🟠 High | 보안 | 반복 로그인 실패 | 긴급 (15-60분) |
| 5. JWT 토큰 만료 | 🟡 Medium | 애플리케이션 | 401 에러 급증 | 우선 (1-4시간) |
| 6. 권한 상승 시도 | 🔴 Critical | 보안 | 반복 403 에러 | 즉시 (0-15분) |
| 7. 메모리 누수 | 🟠 High | 인프라 | 메모리 증가, 성능 저하 | 긴급 (15-60분) |
| 8. 입력 검증 실패 | 🟢 Low | 애플리케이션 | 400 에러 패턴 | 일반 (4-24시간) |

---

## 다중 에이전트 분석 전략

### 에이전트 역할 분담 (예시)

1. **로그 수집 에이전트**
   - 로그 파일 읽기 및 파싱
   - 타임스탬프, 레벨, 메시지 추출

2. **패턴 분석 에이전트**
   - 에러 패턴 식별
   - 시간대별 추세 분석
   - 이상 징후 탐지

3. **보안 분석 에이전트**
   - XSS, SQL Injection 시도 탐지
   - 무차별 대입 공격 식별
   - 권한 위반 모니터링

4. **성능 분석 에이전트**
   - 응답 시간 분석
   - 리소스 사용량 모니터링
   - 병목 지점 식별

5. **종합 보고서 생성 에이전트**
   - 다른 에이전트의 분석 결과 통합
   - 심각도 평가
   - 권장 조치 사항 작성
   - 최종 보고서 생성

---

## 다음 단계

1. ✅ 시나리오 문서 작성 완료
2. ⏭️ 각 시나리오별 실제 로그 데이터셋 생성
3. ⏭️ 데이터셋 검증 및 테스트
4. ⏭️ 에이전트 시스템 설계
5. ⏭️ LangGraph 구현

---

## 참고 문서

- [MNU OUTSIDE API 분석 보고서](./MNU_OUTSIDE_API_ANALYSIS.md)
- [프로젝트 개요](../PROJECT_OVERVIEW.md)
