# Frontend 기동 가이드

## 환경 요구사항

- Node.js 14 이상
- npm 6 이상

## 시작하기

### 1. 의존성 설치

프로젝트 루트에서 frontend 디렉토리로 이동 후 패키지를 설치합니다.

```bash
cd frontend
npm install
```

### 2. 환경 변수 설정

`.env` 파일에서 API URL을 확인하세요:

```
REACT_APP_API_URL=http://localhost:5000
```

### 3. 개발 서버 실행

```bash
npm start
```

실행 후 브라우저에서 자동으로 `http://localhost:3000`이 열립니다.

### 4. 백엔드 서버 연동

프론트엔드가 백엔드 API와 통신하려면 Flask 서버를 먼저 실행해야 합니다.

```bash
# 별도 터미널에서
cd plamingo
python main.py
```

기본적으로 `https://localhost:8080`에서 Flask 서버가 HTTPS로 실행됩니다.

> **참고**: Flask는 현재 `localhost+2.pem`, `localhost+2-key.pem` 인증서를 사용하여 HTTPS로 실행됩니다. 브라우저에서 "안전하지 않음" 경고가 나타나면 "고급" > "계속 진행"을 클릭하거나, 아래 HTTPS 인증서 설정 가이드를 참고하세요.

## 주요 스크립트

| 명령어          | 설명                               |
| --------------- | ---------------------------------- |
| `npm start`     | 개발 서버 실행 (포트 3000)         |
| `npm run build` | 프로덕션 빌드 생성 (`build/` 폴더) |
| `npm test`      | 테스트 실행                        |

## 기술 스택

- React 19.2
- Tailwind CSS 3.4
- React Hooks (useState, useEffect, useRef)
- Web Audio API

## 주요 기능

- 회의 정보 입력 폼
  - 회의 제목, 내용
  - 작성자 정보 (이름, 직급, 이메일)
  - 참석자 관리 (동적 추가/삭제)
- 실시간 오디오 녹음
- 백엔드 API 연동

## HTTPS 개발 환경 설정 (선택사항)

현재 프로젝트의 `plamingo/` 폴더에 있는 `localhost+2.pem` 인증서는 **로컬 환경에서만 유효**합니다. 다른 개발자 또는 새로운 환경에서는 브라우저 신뢰 경고가 발생할 수 있습니다.

### mkcert로 신뢰할 수 있는 인증서 생성하기

브라우저에서 신뢰할 수 있는 개발용 인증서를 생성하려면 `mkcert`를 사용하세요.

#### 1. mkcert 설치

```bash
# macOS (Homebrew)
brew install mkcert nss

# Ubuntu/Debian
sudo apt install libnss3-tools
brew install mkcert

# Windows (Chocolatey)
choco install mkcert
```

#### 2. 로컬 CA 설치

```bash
mkcert -install
```

이 명령어는 로컬 인증 기관(CA)을 생성하고 시스템에 신뢰할 수 있도록 설치합니다.

#### 3. localhost용 인증서 생성

```bash
cd plamingo
mkcert localhost 127.0.0.1 ::1
```

다음 파일이 생성됩니다:

- `localhost+2.pem` (인증서)
- `localhost+2-key.pem` (개인키)

#### 4. Flask에서 인증서 사용

`plamingo/main.py` 파일의 마지막 부분을 확인하세요:

```python
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080,
        ssl_context=('localhost+2.pem', 'localhost+2-key.pem'),
    )
```

이미 `localhost+2.pem` 파일을 사용하도록 설정되어 있습니다. 인증서를 재생성한 후 Flask 서버를 재시작하면 브라우저 경고 없이 HTTPS 연결이 가능합니다.

#### 5. .gitignore 확인

인증서 파일은 개인 환경마다 다르므로 Git에 커밋하지 않는 것이 좋습니다:

```gitignore
# HTTPS certificates
*.pem
```

---

# Slack 알림 설정

회의록 생성 완료 시 Slack 채널로 알림을 받으려면 Slack Bot Token이 필요합니다.

### Slack Bot Token 발급 방법

#### 1. Slack App 생성

1. [Slack API 사이트](https://api.slack.com/apps)에 접속
2. **"Create New App"** 클릭
3. **"From scratch"** 선택
4. App 이름 입력 (예: `Plamingo Meeting Bot`)
5. 워크스페이스 선택 후 **"Create App"** 클릭

#### 2. Bot Token Scopes 설정

1. 좌측 메뉴에서 **"OAuth & Permissions"** 클릭
2. **"Scopes"** 섹션의 **"Bot Token Scopes"**로 이동
3. 다음 권한들을 추가:
   - `chat:write` - 메시지 전송
   - `chat:write.public` - 공개 채널에 메시지 전송
   - `files:write` - 파일 업로드 (선택사항)

#### 3. 워크스페이스에 앱 설치

1. 같은 페이지 상단의 **"OAuth Tokens for Your Workspace"** 섹션으로 이동
2. **"Install to Workspace"** 버튼 클릭
3. 권한 확인 후 **"허용"** 클릭
4. **"Bot User OAuth Token"** 복사 (형식: `xoxb-...`)

#### 4. 환경 변수 설정

`plamingo/.env` 파일에 토큰 추가:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here // 발급받은 토근
SLACK_CHANNEL=#테스트 // Slack 채널명

SLACK_TEAM_ID=C1234567890 // 워크스페이스 ID

SLACK_MCP_SERVER_COMMAND=npx
SLACK_MCP_SERVER_ARGS=-y @modelcontextprotocol/server-slack
```

**채널 ID 확인 방법:**

1. Slack 앱에서 알림을 받을 채널 열기
2. 채널 이름 클릭 → 하단 **"채널 정보"** 확인
3. 채널 ID 복사 (예: `C1234567890`)

또는 채널에서 우클릭 → **"링크 복사"** → URL에서 마지막 부분이 채널 ID

#### 5. 봇을 채널에 초대

1. Slack에서 알림을 받을 채널로 이동
2. 채널에서 `/invite @Plamingo Meeting Bot` 입력
3. 또는 채널 정보 → **"통합"** → **"앱 추가"**에서 봇 선택

### 테스트

Flask 서버를 재시작하고 회의록을 생성한 후 Slack 채널에 알림이 오는지 확인하세요.

---

## 문제 해결

### 의존성 설치 오류

node_modules를 삭제하고 재설치:

```bash
rm -rf node_modules package-lock.json
npm install
```

### HTTPS 인증서 오류

브라우저에서 "NET::ERR_CERT_AUTHORITY_INVALID" 오류가 발생하면:

1. 위의 **HTTPS 개발 환경 설정** 가이드를 따라 mkcert로 인증서를 재생성하세요.
2. `mkcert -install`을 실행했는지 확인하세요.
3. Flask 서버를 재시작하세요.
