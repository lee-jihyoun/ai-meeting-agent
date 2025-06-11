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
    
    # 출력 예시 결과
    <!DOCTYPE html>
    <html lang="ko">
    <head>
    <meta charset="UTF-8">
    <title>프로젝트 알파 v2.3 스프린트 회의록</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.5; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 16px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        h1, h2 { margin-top: 32px; }
    </style>
    </head>
    <body>

    <h1>프로젝트 알파 v2.3 스프린트 회의록</h1>

    <table>
    <tr><th>항목</th><th>내용</th></tr>
    <tr><td><strong>날짜</strong></td><td>2025년&nbsp;06월&nbsp;12일&nbsp;10:00</td></tr>
    <tr><td><strong>작성자</strong></td><td>김지현&nbsp;/&nbsp;선임&nbsp;/&nbsp;kimjh@example.com</td></tr>
    <tr>
        <td><strong>참석자</strong></td>
        <td>
        박수영&nbsp;/&nbsp;책임&nbsp;/&nbsp;PM<br>
        이준호&nbsp;/&nbsp;선임&nbsp;/&nbsp;백엔드 개발<br>
        최유진&nbsp;/&nbsp;전임&nbsp;/&nbsp;프론트엔드<br>
        윤석민&nbsp;/&nbsp;전임&nbsp;/&nbsp;QA<br>
        정해린&nbsp;/&nbsp;주임&nbsp;/&nbsp;DevOps
        </td>
    </tr>
    </table>

    <h2>안건(목적)</h2>
    <ul>
    <li>프로젝트 알파&nbsp;v2.3 출시 전 <strong>잔여 버그·성능 병목</strong> 해소 방안 공유</li>
    <li>차주 스프린트 동안 <strong>우선 대응할 작업 항목</strong> 확정</li>
    </ul>

    <h2>협의(논의) 사항</h2>
    <ol>
    <li><strong>API 응답 지연 원인 분석</strong>
        <ul>
        <li>DB 인덱스 누락 2건(Orders, Logs) 발견 &nbsp;→&nbsp; <em>백엔드&nbsp;팀</em> 즉시 수정 예정</li>
        <li>캐시 미스율 15 % → Redis TTL 재조정 필요</li>
        </ul>
    </li>
    <li><strong>프론트엔드 번들 크기 최적화</strong>
        <table>
        <tr><th>라이브러리</th><th>현재</th><th>목표</th></tr>
        <tr><td>chart.js</td><td>180 KB</td><td>110 KB(트리셰이킹)</td></tr>
        <tr><td>moment.js</td><td>67 KB</td><td>대체 = dayjs (9 KB)</td></tr>
        </table>
    </li>
    <li><strong>배포 파이프라인 안정화</strong>
        <ul>
        <li>GitHub Actions → Azure DevOps 이관 후 첫 배포: 6/14&nbsp;09:00 예정</li>
        <li>블루/그린 전환 단계에서 헬스 체크 30 초 지연 추가</li>
        </ul>
    </li>
    </ol>

    <h2>결정 사항</h2>
    <ul>
    <li><strong>DB 인덱스 추가 작업</strong>을 6/13&nbsp;오전까지 완료한다.</li>
    <li>프론트엔드 <strong>moment.js → dayjs</strong> 전면 교체 승인.</li>
    <li>배포 전 <strong>로드테스트(500 RPS, 10 분)</strong>를 필수 체크리스트에 추가.</li>
    </ul>

    <h2>Action Item</h2>
    <table>
    <tr><th>담당자</th><th>작업내용</th><th>마감일</th></tr>
    <tr><td>이준호</td><td>Orders·Logs 테이블 인덱스 생성</td><td>2025-06-13</td></tr>
    <tr><td>최유진</td><td>moment.js 삭제·dayjs 도입 PR</td><td>2025-06-14</td></tr>
    <tr><td>정해린</td><td>Azure DevOps 배포 파이프라인 헬스 체크 지연 적용</td><td>2025-06-14</td></tr>
    <tr><td>박수영</td><td>로드테스트 스크립트 작성·검수</td><td>2025-06-15</td></tr>
    <tr><td>윤석민</td><td>자동 회귀 테스트 리그레션 시나리오 확장</td><td>-</td></tr>
    </table>

    </body>
    </html>

    
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
