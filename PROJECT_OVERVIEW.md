# 🤖 Plamingo - AI 기반 회의록 자동화 시스템

**Plamingo**는 Azure AI 서비스와 생성형 AI를 활용하여 회의 음성 파일을 텍스트로 변환하고, 체계적인 회의록을 자동으로 생성하는 시스템입니다. 생성된 회의록은 Slack 알림과 메일로 공유되며, 다음 회의 일정이 있는 경우 구글 캘린더 연동을 통해 자동으로 캘린더에 입력됩니다.

---

## 📋 목차
- [주요 기능](#-주요-기능)
- [시스템 아키텍처](#-시스템-아키텍처)
- [기술 스택](#-기술-스택)
- [주요 워크플로우](#-주요-워크플로우)
- [설치 및 설정](#-설치-및-설정)
- [사용 방법](#-사용-방법)

---

## ✨ 주요 기능

### 1. 음성-텍스트 변환 (STT)
- Azure Speech-to-Text Batch API를 사용한 고품질 음성 인식
- WAV, MP3 등 다양한 오디오 포맷 지원
- Azure Blob Storage에 안전하게 저장

### 2. AI 기반 회의록 자동 생성
- Azure OpenAI (GPT-4o)를 활용한 지능형 회의록 작성
- 회의 정보를 구조화된 JSON 형식으로 추출:
  - 회의 메타데이터 (제목, 날짜, 작성자, 참석자)
  - 회의 목적 및 안건
  - 주요 논의사항 (토픽별 상세 내용)
  - 결정사항
  - Action Items (담당자, 작업내용, 마감일)
- HTML 템플릿 기반의 가독성 높은 회의록 생성

### 3. Slack 알림 연동
- MCP (Model Context Protocol)를 활용한 Slack 메시지 자동 발송
- 회의록 생성 완료 시 실시간 알림
- 회의록 URL 링크 포함으로 즉시 접근 가능

### 4. 구글 캘린더 자동 일정 등록
- 회의록에서 다음 회의 일정 자동 추출
- Google Calendar API를 통한 자동 일정 등록
- 서비스 계정 기반의 안전한 인증

### 5. Azure Logic Apps 연동
- Webhook을 통한 이메일 발송 자동화
- 회의록을 이메일로 팀원들에게 배포

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐
│  프론트엔드        │
│ (recording.html)│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                   Flask 서버 (main.py)                   │
├─────────────────────────────────────────────────────────┤
│  /transcribe   │  /webhook   │  /generate_sas_url       │
└────┬──────┬──────┬──────┬──────┬──────┬────────────┬────┘
     │      │      │      │      │      │            │
     ▼      ▼      ▼      ▼      ▼      ▼            ▼
┌────────┐┌───────┐┌──────┐┌──────┐┌──────┐┌─────────┐┌──────────┐
│ Azure  ││Azure  ││Azure ││Slack ││Google││  Logic  ││  Blob    │
│Speech  ││OpenAI ││ Blob ││ MCP  ││ Cal  ││  Apps   ││ Storage  │
│Service ││GPT-4o ││      ││      ││      ││         ││          │
└────────┘└───────┘└──────┘└──────┘└──────┘└─────────┘└──────────┘
```

### 데이터 흐름

1. **음성 업로드** → Azure Blob Storage (meeting-audio)
2. **STT 처리** → Azure Speech-to-Text Batch API
3. **텍스트 저장** → Azure Blob Storage (meeting-text)
4. **AI 요약** → Azure OpenAI (GPT-4o)
5. **회의록 생성** → HTML 변환 → Blob Storage (meeting-notes)
6. **알림 전송** → Slack MCP
7. **일정 등록** → Google Calendar API
8. **이메일 발송** → Azure Logic Apps

---

## 🛠️ 기술 스택

### Backend
- **Python 3.9+**
- **Flask** - 웹 프레임워크
- **Flask-CORS** - CORS 지원

### Azure Services
- **Azure Speech-to-Text** - 음성 인식
- **Azure OpenAI (GPT-4o)** - 회의록 생성
- **Azure Blob Storage** - 파일 저장
- **Azure Logic Apps** - 워크플로우 자동화

### Integration Services
- **Slack MCP Server** (`@zencoderai/slack-mcp-server`) - Slack 메시지 발송
- **Google Calendar API** - 일정 자동 등록
- **Google OAuth2 Service Account** - 인증

### Libraries
```python
azure-cognitiveservices-speech  # Azure Speech SDK
azure-storage-blob              # Azure Blob Storage
openai                          # Azure OpenAI
google-api-python-client        # Google Calendar API
google-auth                     # Google 인증
python-dotenv                   # 환경변수 관리
requests                        # HTTP 요청
```

---

## 🔄 주요 워크플로우

### 회의록 생성 프로세스 (`/transcribe`)

```python
1. SAS URL 파라미터로 음성 파일 접근
   ↓
2. Azure Speech-to-Text Batch API 호출
   ↓
3. 변환된 텍스트를 Blob Storage에 업로드 (meeting-text)
   ↓
4. Azure OpenAI로 회의록 요약 생성
   - 프롬프트: 회의 정보 + STT 텍스트
   - 응답: 구조화된 JSON
   ↓
5. JSON → HTML 템플릿 변환
   ↓
6. HTML 회의록을 Blob Storage에 업로드 (meeting-notes)
   ↓
7. Slack 알림 전송 (MCP 사용)
   ↓
8. 구글 캘린더 일정 자동 등록
   - 회의록에서 "다음 회의" 일정 추출
   - Google Calendar API로 이벤트 생성
```

### Webhook 프로세스 (`/webhook`)

```python
1. 외부 시스템에서 회의 정보 수신
   ↓
2. Azure Logic Apps로 전달
   ↓
3. Logic Apps에서 이메일 발송
   ↓
4. Slack 알림 전송 (MCP 사용)
```

---

## ⚙️ 설치 및 설정

### 1. 가상환경 설정

```bash
cd ai-meeting-agent
python -m venv venv

# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. Node.js 패키지 설치 (Slack MCP)

```bash
npm install
```

### 4. 환경변수 설정

`plamingo/.env` 파일 생성:

```ini
# Azure Speech Service
AI_SERVICE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AI_SERVICE_KEY=your-key
AI_SERVICE_REGION=koreacentral

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-openai-key
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/

# Azure Blob Storage
BLOB_CONNECTION_STRING=your-blob-connection-string
STORAGE_ACCESS_KEY=your-storage-access-key

# Azure Logic Apps
LOGIC_APP_URL=https://your-logic-app-url

# Slack MCP
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_TEAM_ID=T01234567
SLACK_CHANNEL_ID=C01234567

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_FILE=./google-calendar-credentials.json
GOOGLE_CALENDAR_ID=your-calendar-id@group.calendar.google.com
```

### 5. Google Calendar 서비스 계정 설정

1. Google Cloud Console에서 서비스 계정 생성
2. Calendar API 활성화
3. 서비스 계정 키 (JSON) 다운로드
4. `plamingo/google-calendar-credentials.json`으로 저장
5. 캘린더를 서비스 계정 이메일과 공유

### 6. SSL 인증서 (프로덕션 환경)

```bash
cd plamingo
# 자체 서명 인증서 생성 (개발용)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

---

## 🚀 사용 방법

### 서버 실행

```bash
cd plamingo
python main.py
```

### 웹 인터페이스 접근

```
https://localhost:443/
```

### 회의 녹음 및 업로드

1. 웹 페이지에서 회의 정보 입력:
   - 회의 제목
   - 작성자 정보 (이름, 직급, 이메일)
   - 참석자 정보 (이름, 직급, 역할)
   - 회의 내용

2. "녹음 시작" 버튼 클릭

3. 회의 진행 및 녹음

4. "녹음 중지 및 업로드" 버튼 클릭

5. 자동으로 다음 프로세스 진행:
   - 음성 파일 업로드
   - STT 변환
   - AI 회의록 생성
   - Slack 알림
   - 구글 캘린더 일정 등록



## 🔐 보안 고려사항

### 1. 환경변수 관리
- `.env` 파일은 절대 git에 커밋하지 않음
- `.gitignore`에 `.env` 포함 필수

### 2. Azure 리소스 보안
- Blob Storage는 SAS 토큰으로 제한적 접근
- SAS 토큰 만료 시간: 24시간
- Storage Access Key는 환경변수로 관리

### 3. API 키 보호
- Azure OpenAI API 키는 환경변수로 관리
- Google 서비스 계정 JSON 파일 보호
- Slack Bot Token은 환경변수로 관리

### 4. SSL/TLS
- 프로덕션 환경에서는 HTTPS 필수
- 유효한 SSL 인증서 사용 권장

---

## 🧪 테스트

### 구글 캘린더 연동 테스트

```bash
cd plamingo
python google_calendar.py
```

### Slack 연동 테스트

```bash
cd plamingo
python slack_integration.py
```

---

## 🐛 트러블슈팅

### 1. 구글 캘린더 400 Bad Request
- event body의 날짜 형식 확인 (ISO 8601: `YYYY-MM-DDTHH:MM:SS`)
- 서비스 계정이 캘린더에 대한 권한이 있는지 확인
- `calendarId`가 올바른지 확인

### 2. Slack 메시지 전송 실패
- `SLACK_BOT_TOKEN`, `SLACK_TEAM_ID`, `SLACK_CHANNEL_ID` 확인
- MCP 서버 경로 확인 (`node_modules/@zencoderai/slack-mcp-server/dist/index.js`)
- Slack 앱이 채널에 초대되어 있는지 확인

### 3. Azure Speech-to-Text 오류
- 음성 파일 포맷 확인 (WAV 권장)
- SAS URL 유효성 확인
- Azure 리소스 키 및 엔드포인트 확인
