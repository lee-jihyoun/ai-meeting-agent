# Plamingo Frontend (React)

AI Meeting Agent의 프론트엔드입니다.

## 시작하기

### 1. 의존성 설치
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

브라우저에서 http://localhost:3000 이 자동으로 열립니다.

### 4. 프로덕션 빌드
```bash
npm run build
```

빌드된 파일은 `build/` 폴더에 생성됩니다.

## 백엔드 연동

React 앱이 Flask 백엔드와 통신하려면:

1. Flask 서버를 먼저 실행하세요 (포트 5000):
   ```bash
   cd ../plamingo
   python main.py
   ```

2. React 개발 서버를 실행하세요 (포트 3000):
   ```bash
   cd ../frontend
   npm start
   ```

## 주요 기능

- 회의 정보 입력 (제목, 내용, 작성자, 참석자)
- 실시간 오디오 녹음
- WAV 파일 Azure Blob Storage 업로드
- 회의록 자동 생성 및 Slack 알림

## 기술 스택

- React 18
- React Hooks (useState, useEffect, useRef)
- Web Audio API (마이크 녹음)
- Fetch API (백엔드 통신)
