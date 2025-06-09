import os, json, textwrap, datetime as dt
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI, OpenAIError

# ─────────────────── 환경 변수 로딩 ───────────────────
load_dotenv()   # .env 파일에 ① AZURE_OPENAI_API_KEY ② AZURE_OPENAI_ENDPOINT
                # ③ BLOB_CONNECTION_STRING ④ CONTAINER_NAME ⑤ BLOB_NAME 등

# TODO: meeting-text 컨테이너에서 회의록 작성 완료된 blob은 별도 컨테이너로 이동
container_name = "meeting-text"
blob_name = "2025-05-26_meeting.txt"

# ─────────────────── 1) Blob에서 STT 원문 가져오기 ───────────────────
blob_service = BlobServiceClient.from_connection_string(
    os.getenv("BLOB_CONNECTION_STRING"))
# blob_client  = blob_service.get_container_client(
#     os.getenv("CONTAINER_NAME")).get_blob_client(os.getenv("BLOB_NAME"))

# print("blob_service: ", blob_service)

blob_client  = blob_service.get_container_client(
    container_name).get_blob_client(blob_name)

# print("blob_client: ", blob_client)

stt_text = blob_client.download_blob().content_as_text()
print("STT 원문 일부 ↓\n", stt_text[:200], "...\n")

# TODO: meeting-text 컨테이너에서 info.json에서 읽어올 수 있도록 준비
# ─────────────────── 2) 회의 메타데이터 준비 ───────────────────
meeting_meta = {
    "title"      : "프로젝트 플라밍고 킥오프",
    "datetime"   : f"{dt.datetime.now():%Y년 %m월 %d일 %H:%M}",
    "writer"     : "김지현/선임/kimjh@example.com",
    "attendees"  : "박수영/책임/PM, 이준호/선임/개발, 최유진/전임/디자인",
}

# TODO: 프롬프트 다듬으면서 테스트하기
# ─────────────────── 3) 프롬프트 작성 ───────────────────
SYSTEM_MSG = "당신은 회의록 전문 작성자입니다."
USER_PROMPT_TEMPLATE = """
#명령문
당신은 회의록 전문 작성자입니다. 다음 회의 대화 내용을 분석하여 구조화된 회의록으로 정리해주세요.

#제약조건
- 회의 주제, 날짜, 작성자, 참석자 정보를 상단에 표로 정리하여 표시
- 날짜 정보를 YYYY년 MM월 DD일 HH:MM ~ HH:MM 형태로 작성
- 작성자를 이름/직급/이메일 형태로 작성
- 참석자 명단을 이름/직급/역할 형태로 작성
- 주요 목적은 회의 배경, 회의 목적, 회의 안건 순으로 정리
- 주요 논의 사항을 논리적인 순서로 정리
- 중요한 결정사항을 별도로 강조 
- 할당된 작업 및 담당자를 명확히 표시
- 후속조치 및 마감일을 표로 정리
- 전체 내용을 600단어 이내로 요약

#입력문
회의 제목 : {title}
회의 내용 : {content}
날짜 : {datetime}
작성자 : {writer}
참석자 : {attendees}

#출력형식
# {title} 회의록
**날짜** : {datetime}
**작성자** : {writer} = 이름/직급/이메일 형태로 표시
**참석자** : {attendees} = 이름/직급/역할 형태로 표시

## 주요 목적
1. 회의 배경
2. 회의 목적
3. 회의 안건

## 주요 논의 사항
1. [주제 1]
 - [세부 내용]
 - [세부 내용]
2. [주제 2]
 - [세부 내용]
 - [세부 내용]

## 주요 결정사항
- [결정사항 1]
- [결정사항 2]

## 액션 아이템
| 담당자 | 작업내용 | 마감일 |
|-------|---------|-------|
| [이름] | [작업]  | [날짜]|
| [이름] | [작업]  | [날짜]|

## 다음 회의
**날짜** : [날짜]
**안건** : [다음 회의 안건]

"""

user_prompt = USER_PROMPT_TEMPLATE.format(
    title     = meeting_meta["title"],
    content   = textwrap.shorten(stt_text, 12000, placeholder="..."),
    datetime  = meeting_meta["datetime"],
    writer    = meeting_meta["writer"],
    attendees = meeting_meta["attendees"]
)

# ─────────────────── 4) Azure OpenAI 호출 ───────────────────
client = AzureOpenAI(
    api_key        = os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version    = "2024-12-01-preview"      # 실제 리소스 페이지에 적힌 버전
)

try:
    resp = client.chat.completions.create(
        model       = "plamingo-gpt-4o",        # ← 포털에서 배포한 Deployment 이름
        temperature = 0.2,
        max_tokens  = 800,
        messages=[
            {"role": "system", "content": SYSTEM_MSG},
            {"role": "user",   "content": user_prompt}
        ]
    )
    summary = resp.choices[0].message.content
    print("\n──────── 요약 결과 ────────\n", summary)
except OpenAIError as e:
    print("OpenAI 호출 오류:", e)
