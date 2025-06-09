# report_api 사용 방법

## 가상환경 실행
### macOS / Linux
위/아래 방법 중 택1

```bash
source venv/bin/activate
pip install --upgrade "openai>=1.14.0"
```

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Windows
```bash
source venv/Scripts/activate
pip install --upgrade "openai>=1.14.0"
```
```bash
source venv/Scripts/activate
pip install -r requirements.txt
```

## .env 설정
아래 3가지 값이 추가로 필요합니다.
```bash
BLOB_CONNECTION_STRING=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
```

## 실행
```bash
python meeting_agent.py
```