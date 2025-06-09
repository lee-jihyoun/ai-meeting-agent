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
# print("STT 원문 일부 ↓\n", stt_text[:200], "...\n")

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
- 전체 내용을 1000단어 이내로 작성
- 출력 예시 결과를 참고하여 작성하며, 예시에 없는 내용은 제외

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

# 출력 예시 결과
# 프로젝트 플라밍고 킥오프 회의록

| **항목**     | **내용**                                  |
|--------------|-------------------------------------------|
| **날짜**     | 2025년 06월 09일 16:08 ~ 17:00           |
| **작성자**   | 김지현/선임/kimjh@example.com            |
| **참석자**     | 박수영/책임/PM                   |
|                | 이준호/선임/개발                 |
|                | 최유진/전임/디자인               |


---

## 주요 목적

1. **회의 배경**
   - 프로젝트 플라밍고의 성공적인 시작을 위해 주요 기술적 과제와 일정 관리 방안을 논의하고, 초기 작업의 우선순위를 설정하기 위함.        

2. **회의 목적**
   - 데이터 이전 작업의 세부 계획 수립
   - 다운타임 최소화를 위한 전략 논의
   - 각 담당자의 역할과 책임 명확화

3. **회의 안건**
   - 데이터 이전 작업의 단계별 계획
   - 다운타임 고려 사항 및 해결 방안
   - 작업 요청 및 진행 상황 점검

---

## 주요 논의 사항

1. **데이터 이전 작업의 단계별 계획**
   - **비변동 데이터 우선 이전**: 6년간의 비변동 데이터를 먼저 이전하는 것이 효율적이라는 의견이 제시됨.
   - **변동 데이터 처리**: 변동 데이터는 다운타임 기간에 이전하는 것으로 합의.

2. **다운타임 최소화를 위한 전략**
   - 다운타임을 최소화하기 위해 데이터 이전 작업의 정확한 산정이 필요함.
   - 이이령 선임이 요청한 데이터 산정 결과가 아직 확인되지 않아, 이를 우선적으로 검토해야 함.

3. **작업 요청 및 진행 상황 점검**
   - TA 팀에서 전체 용량 조사를 진행했으나, 용량 초과 문제가 발생.
   - 해당 문제는 지난주에 요청되었으나 아직 해결되지 않아 추가적인 검토가 필요함.

---

## 주요 결정사항

- 비변동 데이터는 사전에 이전하고, 변동 데이터는 다운타임 기간에 처리하기로 결정.
- 데이터 용량 초과 문제는 TA 팀과 협력하여 해결 방안을 마련하기로 함.
- 이이령 선임이 요청한 데이터 산정 결과를 빠르게 확인하여 작업을 진행하기로 함.

---

## 액션 아이템

| **담당자** | **작업내용**                              | **마감일**         |
|------------|-------------------------------------------|--------------------|
| 이이령     | 데이터 산정 결과 확인 및 보고              | 2025년 06월 12일  |
| TA 팀      | 데이터 용량 초과 문제 해결 방안 마련        | 2025년 06월 14일  |
| 김지현     | 데이터 이전 작업 세부 일정 재조정           | 2025년 06월 15일  |

---

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
