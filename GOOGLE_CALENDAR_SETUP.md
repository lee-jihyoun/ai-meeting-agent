# 구글 캘린더 연동 설정 가이드

회의록에서 다음 회의 일정을 추출하여 자동으로 구글 캘린더에 저장하는 기능입니다.

## 기능 개요

- 회의록 생성 시 Action Items에서 다음 회의 일정을 자동 감지
- 감지된 일정을 구글 캘린더에 자동으로 이벤트로 등록
- 서비스 계정 방식으로 간편하게 설정

---

## 설정 방법 (2단계)

### 1단계: Google Cloud Console 설정

#### 1-1. 프로젝트 생성 및 API 활성화

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
   - 프로젝트 이름 예: `meeting-calendar-mcp`
3. **API 및 서비스 > 라이브러리** 이동
4. **"Google Calendar API"** 검색 후 **사용 설정** 클릭

#### 1-2. 서비스 계정 생성

1. **API 및 서비스 > 사용자 인증 정보** 이동
2. **+ 사용자 인증 정보 만들기** 클릭
3. **서비스 계정** 선택
4. 서비스 계정 세부정보 입력:
   - 이름: `calendar-integration`
   - ID: 자동 생성됨
   - 설명: `Meeting calendar integration service account`
5. **만들기 후 계속** 클릭
6. 역할 선택: **건너뛰기** (기본 권한 사용)
7. **완료** 클릭

#### 1-3. 서비스 계정 키 생성

1. 생성된 서비스 계정 클릭
2. **키** 탭으로 이동
3. **키 추가 > 새 키 만들기** 클릭
4. 키 유형: **JSON** 선택
5. **만들기** 클릭 → JSON 파일 자동 다운로드
   - 파일명 예: `meeting-calendar-mcp-abc123.json`

#### 1-4. 캘린더 공유 설정

**중요**: 서비스 계정에 캘린더 접근 권한을 부여해야 합니다.

1. [Google Calendar](https://calendar.google.com/) 웹 접속
2. 왼쪽 사이드바에서 사용할 캘린더 옆 **⋮** (더보기) 클릭
3. **설정 및 공유** 선택
4. **특정 사용자와 공유** 섹션으로 스크롤
5. **사용자 추가** 클릭
6. 서비스 계정 이메일 입력
   - 예: `calendar-integration@meeting-calendar-mcp.iam.gserviceaccount.com`
   - 이메일은 다운로드한 JSON 파일의 `client_email` 필드에서 확인 가능
7. 권한: **변경 및 공유 관리 권한** 선택
8. **전송** 클릭

---

### 2단계: JSON 파일 설정

#### 2-1. JSON 파일 복사

다운로드한 JSON 파일을 프로젝트의 `plamingo` 디렉토리로 복사하고 파일명을 변경:

```bash
# 다운로드한 파일을 복사
cp ~/Downloads/meeting-calendar-mcp-abc123.json /Users/nakyoung/Desktop/ktds/2025/ai-meeting-agent/plamingo/google-calendar-credentials.json
```

#### 2-2. 환경 변수 확인

`plamingo/.env` 파일에 다음이 이미 설정되어 있는지 확인:

```bash
# Google Calendar Configuration (서비스 계정 방식 - 간단함!)
# Google Calendar API 서비스 계정 JSON 파일 경로
GOOGLE_CALENDAR_CREDENTIALS_FILE=/Users/nakyoung/Desktop/ktds/2025/ai-meeting-agent/plamingo/google-calendar-credentials.json
GOOGLE_CALENDAR_ID=primary
```

---

## 설치 완료 확인

모든 설정이 완료되었습니다! 다음을 확인하세요:

```bash
# JSON 파일이 있는지 확인
ls -la plamingo/google-calendar-credentials.json

# .env 파일에 설정이 있는지 확인
grep GOOGLE_CALENDAR_CREDENTIALS plamingo/.env
```

---

## 사용 방법

설정이 완료되면 회의록 생성 시 자동으로 다음 회의 일정을 캘린더에 추가합니다.

### 회의록에서 다음 회의 일정 감지 조건

다음 조건을 만족하면 자동 감지됩니다:

1. **Action Items**에 다음 키워드 중 하나가 포함:
   - "다음 회의"
   - "차기 회의"
   - "후속 회의"
   - "next meeting"

2. 날짜 정보는 **YYYY-MM-DD** 형식으로 작성

### 예시

회의 중 발언: "다음 회의는 12월 10일에 진행하겠습니다."

→ AI가 회의록 작성 시 Action Items에 자동 포함:

| 담당자 | 작업내용 | 마감일 |
|-------|--------|-------|
| 홍길동 | 다음 회의 일정 조율 | 2025-12-10 |

→ 시스템이 자동으로 구글 캘린더 이벤트 생성:
- **제목**: "원래 회의 제목 - 후속 회의"
- **날짜**: 2025-12-10 10:00-11:00 (KST)
- **설명**: "다음 회의 안건: 다음 회의 일정 조율"
- **캘린더**: 공유 설정한 캘린더

---

## 동작 확인

애플리케이션 실행 시 로그에서 다음 메시지를 확인할 수 있습니다:

```bash
# 성공 시
✅ 구글 캘린더 인증 완료
✅ 캘린더 이벤트 생성 완료: https://calendar.google.com/calendar/event?eid=...
✅ 구글 캘린더 이벤트 생성 성공: https://calendar.google.com/calendar/event?eid=...

# 다음 회의 일정이 없는 경우
ℹ️ 구글 캘린더 이벤트 미생성: 회의록에서 다음 회의 일정을 찾을 수 없습니다.

# 인증 오류
⚠️ 구글 캘린더 처리 중 오류 (무시하고 계속): ...
```

---

## 문제 해결

### 서비스 계정 파일을 찾을 수 없습니다

**원인**: JSON 파일 경로가 잘못되었거나 파일이 없음

**해결방법**:
1. `plamingo/google-calendar-credentials.json` 파일이 있는지 확인
2. `.env` 파일의 `GOOGLE_CALENDAR_CREDENTIALS_FILE` 경로 확인
3. 경로가 절대 경로로 올바르게 설정되었는지 확인

### PEM 파일 파싱 오류

**원인**: JSON 파일의 `private_key` 값이 손상되었거나 잘못된 형식

**해결방법**:
1. Google Cloud Console에서 새 키를 다시 생성
2. 다운로드한 JSON 파일을 **직접 복사** (내용을 복사/붙여넣기 하지 말고 파일 자체를 복사)
3. JSON 파일을 텍스트 에디터로 열어서 `private_key` 필드가 제대로 있는지 확인

### 캘린더 이벤트가 생성되지 않음

**확인사항**:
1. 회의록의 Action Items에 "다음 회의" 키워드 포함 여부
2. 날짜가 YYYY-MM-DD 형식인지 확인
3. 서비스 계정에 캘린더 공유 권한이 있는지 확인
   - Google Calendar > 설정 및 공유 > 특정 사용자와 공유 확인

### 권한 오류 (403 Forbidden)

**해결방법**:
1. Google Calendar에서 서비스 계정 이메일이 공유되어 있는지 확인
2. 권한이 "변경 및 공유 관리 권한"으로 설정되어 있는지 확인
3. 캘린더 공유 설정 후 5-10분 정도 기다린 후 재시도

---

## 테스트

수동으로 캘린더 연동 테스트:

```bash
cd plamingo
python google_calendar.py
```

테스트 코드가 실행되어 2025-12-10에 샘플 이벤트가 생성됩니다.

---

## 기능 비활성화

구글 캘린더 연동을 사용하지 않으려면:

```bash
# .env 파일에서 다음 줄들을 주석 처리
# GOOGLE_CALENDAR_CREDENTIALS_FILE=...
# GOOGLE_CALENDAR_ID=...
```

기능이 비활성화되어도 회의록 생성은 정상적으로 진행됩니다.

---

## 보안 고려사항

- 다운로드한 JSON 키 파일은 **절대 Git에 커밋하지 마세요**
- `.gitignore`에 추가되어 있는지 확인:
  ```
  google-calendar-credentials.json
  ```
- 서비스 계정 키는 민감한 정보이므로 안전하게 보관
- 프로덕션 환경에서는 환경 변수나 비밀 관리 시스템 사용 권장

---

## 다음 단계

1. 회의를 진행하고 녹음
2. 회의록 생성 시 "다음 회의는 X월 X일에 진행하겠습니다" 언급
3. 자동으로 구글 캘린더에 이벤트 생성
4. [Google Calendar](https://calendar.google.com/)에서 확인!

---

## 추가 도움말

- [Google Calendar API 문서](https://developers.google.com/calendar/api/guides/overview)
- [서비스 계정 키 관리 가이드](https://cloud.google.com/iam/docs/service-account-creds)
