# 🧠 AI Meeting Agent

Azure Speech-to-Text, Document Intelligence 등을 활용해 회의 내용을 자동으로 수집하고 요약하는 AI 기반 어시스턴트입니다.

---

## 🚀 사용 기술 스택

| 분류 | 기술 |
|------|------|
| 언어 | Python 3.12 |
| 가상환경 | venv |
| 환경변수 관리 | python-dotenv |
| 음성 인식 | Azure Speech-to-Text (azure-cognitiveservices-speech) |
| 문서 인식 (OCR) | Azure Document Intelligence (azure-ai-formrecognizer) |
| 클라우드 서비스 | Azure Cognitive Services (Speech, Form Recognizer) |
| 파일 저장 | 로컬 디렉토리 / Blob Storage (선택적) |
| 워크플로우 자동화 | Logic Apps (계획 중) |

---

## 1. 가상환경 생성

### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

### Windows
```bash
python -m venv venv
source venv/Scripts/activate
```
※ 가상환경은 ai-meeting-agent/ 최상위 폴더에 생성합니다.

## 2. 패키지 설치
가상환경을 활성화한 후에 가상환경 내에 패키지를 설치합니다.

```bash
cd ai-meeting-agent
pip install -r requirements.txt
```

## 3. .env 파일 생성
각 서비스 폴더(speech-service/, ocr-service/)에 .env 파일을 생성하고 다음과 같이 입력하세요:
```ini
AI_SERVICE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AI_SERVICE_KEY=your-key
AI_SERVICE_REGION=koreacentral
```

## 4. 서비스 실행

### Speech-to-Text 실행

```bash
cd speech-service
python speech-service.py
```

### Document Intelligence 실행

```bash
cd ocr-service
python document-intelligence.py
```

## 🛑 주의사항
- venv/, .env, docs/ 폴더는 .gitignore에 포함되어야 합니다.
- 리소스 키, 엔드포인트 등은 외부에 노출되지 않도록 주의하세요.