# Azure Document Intelligence

# 1. 리소스 생성

- 구 form recognizer
- 리브랜딩 한 Document intelligence를 사용 중임 (패키지에는 form recognizer 가 남아 있음)

![rg-ocr-demo.png](./img/rg-ocr-demo.png)

# 2. sdk 방식

```bash
pip install azure-ai-formrecognizer
```

# 3. 실행 방법 및 코드 설명
- ocr-serivce 하위에 docs, images 폴더 생성 후 ocr 하고 싶은 이미지, 문서를 넣습니다.
- 아래 나와있는 포맷 내에서 ocr 가능합니다.
```bash
# 이미지 폴더 경로 지정
image_folder = "./docs/images"  # OCR할 이미지가 들어 있는 로컬 폴더
supported_formats = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".pdf"]
```
- README.md 파일을 참고하여 서비스를 실행합니다.

# 4. 실행 결과
- 프로젝트 설명을 한 아키텍처를 ocr 하는 기능을 수행했습니다.
- 이미지 내 텍스트나 표를 잘 읽습니다.
```
📄 처리 중: image1.png
📄 페이지 1:
🔹 {}
🔹 logic apps
🔹 o
🔹 음성 인식
🔹 Speech to text
🔹 텍스트 전사
🔹 cognitive search
🔹 openai service
🔹 O
🔹 회의록 요약
🔹 voice
🔹 Transcript
🔹 blob storage
🔹 메일 발송
🔹 실시간 질의응답
🔹 Azure Al Bot

📄 처리 중: image2.png
📄 페이지 1:
🔹 서비스
🔹 Azure Speech to Text (음성 인식)
🔹 1시간 실시간 음성 전사 비용
🔹 $1.00
🔹 Azure Document Intelligence (이미지 인식)
🔹 이미지 1,000개당 $1.50
🔹 1시간 회의 중 1분당 캡처, 60장 가정
🔹 60개당 $0.09
🔹 Azure OpenAl (GPT-4 8k 요약)
🔹 회의록
🔹 10 * $0.03 + 1 * $0.06
🔹 = $0.36
🔹 Azure OpenAl (GPT-4 8k 기준)
🔹 Q&A
🔹 Azure Cognitive Search + Azure OpenAl
🔹 프로비저닝, 1시간당 과금, S1 기준
🔹 $0.336
🔹 Azure Logic Apps (워크플로우 실행)
🔹 프로세스 실행 1회
🔹 $0.000125 (매우 적은 비용)
🔹 Azure Blob Storage
🔹 음성 파일 1건, 텍스트 파일 1건
🔹 1시간 회의 기준 약 ~$2.10 예상
🔹 사용량(EastUS)
🔹 프롬프트 10,000토큰 + 응답 1,000토큰으로
🔹 가정
🔹 프롬프트 500토큰 + 응답 200토큰으로 가정
🔹 0.5 * $0.03 + 0.2 * $0.06
🔹 = $0.027, 질문 10개당 0.27$
🔹 예상 비용
🔹 콜드존 기준 보관 $0.0036/GB
🔹 읽기 작업 10,000건당 $0.234
🔹 쓰기 작업 10,000건당 $0.13
```