import os, json, textwrap, datetime as dt
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI, OpenAIError


# blob에 업로드: .wav, .txt, .json. .md -> blob에 올라간 txt를 그대로 ai가 사용
def summarize_meeting_notes(info, file_name):
    print("AI가 요약을 시작합니다.")
    # ─────────────────── 환경 변수 로딩 ───────────────────
    load_dotenv()   # .env 파일에 ① AZURE_OPENAI_API_KEY ② AZURE_OPENAI_ENDPOINT
                    # ③ BLOB_CONNECTION_STRING ④ CONTAINER_NAME ⑤ BLOB_NAME 등

    # TODO: meeting-text 컨테이너에서 회의록 작성 완료된 blob은 별도 컨테이너로 이동
    container_name = "meeting-text"

    # ─────────────────── 1) Blob에서 STT 원문 가져오기 ───────────────────
    blob_service = BlobServiceClient.from_connection_string(os.getenv("BLOB_CONNECTION_STRING"))

    blob_client = blob_service.get_container_client(container_name).get_blob_client(file_name+'.txt')
    # print("blob_client: ", blob_client)

    stt_text = blob_client.download_blob().content_as_text()
    # print("STT 원문 일부 ↓\n", stt_text[:200], "...\n")

    # ─────────────────── 2) 회의 메타데이터 준비 ───────────────────
    meeting_meta = {
        "title"      : info['title'],
        "datetime"   : info['startTime'],
        "writer"     : info['writer'],
        "attendees"  : info['attendees'],
    }

    # TODO: 프롬프트 다듬으면서 테스트하기
    # ─────────────────── 3) 프롬프트 작성 ───────────────────
    SYSTEM_MSG = "당신은 회의록 전문 작성자입니다."
    USER_PROMPT_TEMPLATE = """
    # 시스템 지시
    당신은 회의록 전문 작성자입니다.

    # 제약조건
    1. 상단에 **회의 주제·날짜·작성자·참석자**를 표로 정리  
        - 날짜: **YYYY년 MM월 DD일 HH:MM** 형식 
        - 작성자: `이름/직급/이메일`  
        - 참석자: `이름/직급/역할` 형식, 한 줄당 한 명 
    2. 안건(목적), 협의(논의)사항, 결정사항, Action Item 순으로 정리
    3. **안건(목적)** 섹션은 **회의 배경·목적**을 합쳐 2줄 내로 요약  
    4. **협의(논의) 사항** 
        - 구체적·자세한 논의를 **논리적 순서**로 번호 매김  
        - 가독성이 좋다면 표 사용 가능  
    5. **결정 사항**은 굵은 글머리(**•**) 목록으로 강조   
    6. **Action Item** 섹션은 항상 표시
        - 표 형태 | 담당자 | 작업내용 | 마감일 |
        - 정보가 없으면 셀에 `-` 표기  
    7. 제공된 입력 정보만 사용하고, 존재하지 않는 내용은 **추정·창작하지 마세요.**
    8. 전체 분량은 **1 000단어 이내**로 제한
    9. 최종 결과물은 html 파일로 변환 
    
    # 입력
    회의 제목 : {title}
    회의 내용 : {content}
    날짜 : {datetime}
    작성자 : {writer}
    참석자 : {attendees}
    
    # 출력형식 (html)
    # {title} 회의록
    | **항목** | **내용** |
    |----------|----------|
    | **날짜** | {datetime} |
    | **작성자** | {writer} | 
    | **참석자** | {attendees} |
    
    ---

    ## 안건(목적)
    - [배경·목적 2줄 요약]

    ---
    
    ## 협의(논의) 사항
    1. **[주제 1]**
    - 세부 내용
    - 세부 내용
    2. **[주제 2]**
    - 세부 내용
    - 세부 내용

    ---
    
    ## 결정 사항
    • [결정 1]  
    • [결정 2]

    ---
    
    ## Action Item
    | 담당자 | 작업내용 | 마감일 |
    |-------|--------|-------|
    |  이름  |   작업  |  날짜  |
    |  이름  |   작업  |  날짜  |
    
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
        # print("\n──────── 요약 결과 ────────\n", summary)
        return summary

    except OpenAIError as e:
        print("OpenAI 호출 오류:", e)
