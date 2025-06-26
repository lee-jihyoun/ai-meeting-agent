import os, json, textwrap, datetime as dt
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from openai import AzureOpenAI, OpenAIError

# 현재 파일 기준으로 .env의 절대경로 생성
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path)


# blob에 업로드: .wav, .txt, .json. .md -> blob에 올라간 txt를 그대로 ai가 사용
def summarize_meeting_notes(info, file_name):
    print("AI가 요약을 시작합니다.")
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
        - 참석자: `이름/직급/역할` 형식
    2. 참석자가 여러명인 경우 표의 행이 추가되며 한 줄 당 한 명이 들어감
    2. 안건(목적), 협의(논의)사항, 결정사항, Action Item 순으로 정리
    3. **안건(목적)** 섹션은 **회의 배경·목적**을 합쳐 2줄 내로 요약  
    4. **협의(논의) 사항** 
        - 구체적·자세한 논의를 **논리적 순서**로 번호 매김  
        - 가독성이 좋다면 표 사용 가능  
    5. **결정 사항**은 굵은 글머리(**•**) 목록으로 강조   
    6. **Action Item** 섹션은 항상 표시
        - 표 형태는 아래의 형태로 구성
        | 담당자 | 작업내용 | 마감일 |
        |-------|--------|-------|
        |  이름  |   작업  |  날짜  |
        - 정보가 없으면 셀에 `-` 표기          
    7. 제공된 입력 정보만 사용하고, 존재하지 않는 내용은 **추정·창작하지 마세요.**
    8. 전체 분량은 **1 000단어 이내**로 제한
    9. 최종 결과물은 반드시 유효한 JSON만 출력하라. 
    10. 설명, 주석, 마크다운, 코드펜스, 기타 텍스트를 포함하지 마라.
    11. 모든 필드는 반드시 채워라.
    12. 응답이 길어질 경우, 반드시 JSON 전체를 반환하라.
    13. action_items 등 일부만 반환해도 좋으니 반드시 완전한 JSON만 반환하라
    10. 백틱( ``` ) 코드펜스, Markdown 문법은 절대 사용하지 마라
    11. 최종 결과물의 글자 수는 2000자 이내로 작성하라.
    
    # 입력
    회의 제목 : {title}
    회의 내용 : {content}
    날짜 : {datetime}
    작성자 : {writer}
    참석자 : {attendees}
    
    # 출력형식 (json)
    {{
      "minutes": {{
        "info": {{
          "title": "",
          "date": "",
          "author": {{
            "name": "",
            "position": "",
            "email": ""
          }},
          "attendees": [
            {{
              "name": "",
              "position": "",
              "role": ""
            }}
          ]
        }},
        "main_objectives": {{
          "background": "",
          "objectives": [
            ""
          ],
          "agenda": [
            ""
          ]
        }},
        "main_discussions": [
          {{
            "topic": "",
            "details": [
              ""
            ]
          }}
        ],
        "key_decisions": [
          ""
        ],
        "action_items": [
          {{
            "owner": "",
            "task": "",
            "due_date": ""
          }}
        ]
      }}
    }}


 # 출력 예시
    {{
      "minutes": {{
        "info": {{
          "title": "CAMP구축회의"
          "date": "2025년 06월 13일 14:14",
          "author": {{
            "name": "1",
            "position": "전임",
            "email": "yh.baek@kt.com"
          }},
          "attendees": [
            {{
              "name": "1",
              "position": "전임",
              "role": "1"
            }}
          ]
        }},
        "main_objectives": {{
          "background": "",
          "objectives": [
            "데이터 수집 및 보안 정책 개선 방안 논의",
            "램프 및 캠프 시스템의 개인정보 처리 및 암호화 방안 검토"
          ],
          "agenda": [
            "데이터 수집 및 보안 정책 개선 방안 논의",
            "램프 및 캠프 시스템의 개인정보 처리 및 암호화 방안 검토"
          ]
        }},
        "main_discussions": [
          {{
            "topic": "데이터 수집 및 암호화 방안",
            "details": [
              "현재 램프 시스템에서 수집되는 데이터의 암호화 필요성 검토",
              "페이로드 데이터의 암호화 처리 및 저장 방식 논의",
              "대용량 데이터 추출 및 복호화 처리 방안 검토"
            ]
          }},
          {{
            "topic": "캠프 시스템의 데이터 수집 항목 축소",
            "details": [
              "캠프 시스템에서 비즈니스 모니터링 및 장애 탐지용 데이터만 수집",
              "필수 항목만 수집하도록 가이드라인 설정"
            ]
          }},
          {{
            "topic": "보안 권한 관리",
            "details": [
              "사용자 권한별 데이터 접근 및 다운로드 제한 방안 논의",
              "보안 검토를 통한 권한 부여 절차 강화"
            ]
          }},
          {{
            "topic": "ACA 연동 및 표준 규격 준수",
            "details": [
              "ACA 연동을 위한 표준 규격 설계서 검토",
              "ACA 지원 미비로 인한 대안 및 유예 기간 논의"
            ]
          }}
        ],
        "key_decisions": [
          "램프 시스템의 데이터 암호화 모듈 개발 및 적용 방안 검토",
          "캠프 시스템에서 비필수 데이터 수집 중단 및 가이드라인 마련",
          "사용자 권한별 데이터 접근 제한 및 다운로드 기능 개선",
          "ACA 연동을 위한 표준 규격 준수 및 지원 방안 마련"
        ],
        "action_items": [
          {{
            "owner": "1",
            "task": "램프 시스템 암호화 모듈 개발 소요 시간",
            "due_date": ""
          }}
        ]
      }}
}}

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
            max_tokens  = 4000,
            messages=[
                {"role": "system", "content": SYSTEM_MSG},
                {"role": "user",   "content": user_prompt}
            ]
        )
        summary = resp.choices[0].message.content
        # print("\n──────── 요약 결과 ────────\n", summary)

        # TODO: json 구조가 제대로 생성이 안된 경우 재시도.
        try:
            summary = json.loads(summary)
            # print(summary)
        except Exception as e:
            print(summary)
            print(e)
        return summary

    except OpenAIError as e:
        print("OpenAI 호출 오류:", e)


def make_json_to_html(meeting_json):
    # 현재 파이썬 파일의 위치를 기준으로 경로 생성
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, 'template.html')
    with open(template_path, encoding="utf-8") as f:
        html_template = f.read()

        # 데이터 가공
        info = meeting_json["minutes"]["info"]
        main_objectives = meeting_json["minutes"]["main_objectives"]
        main_discussions = meeting_json["minutes"]["main_discussions"]
        key_decisions = meeting_json["minutes"]["key_decisions"]
        action_items = meeting_json["minutes"]["action_items"]

        # 참석자
        attendees_html = ""
        for i, a in enumerate(info["attendees"]):
            attendees_html += (
                f'<tr>'
                f'<td style="border: 1px solid #333; padding: 8px;">{"<strong>참석자</strong>" if i == 0 else ""}</td>'
                f'<td style="border: 1px solid #333; padding: 8px;">{a["name"]}/{a["position"]}/{a["role"]}</td>'
                f'</tr>\n'
            )

      # 목적/안건
        objectives_html = ""
        if isinstance(main_objectives.get("objectives"), list):
            objectives_html += "\n".join(f"<li>{item}</li>" for item in main_objectives["objectives"])
        elif main_objectives.get("objectives"):
            objectives_html += f"<li>{main_objectives['objectives']}</li>"
        if main_objectives.get("background"):
            objectives_html = f"<li>{main_objectives['background']}</li>\n" + objectives_html

        # 논의사항
        discussions_html = ""
        for d in main_discussions:
            details = "".join(f"<li>{detail}</li>" for detail in d["details"])
            discussions_html += f'<li><strong>{d["topic"]}</strong><ul>{details}</ul></li>\n'

        # 결정사항
        decisions_html = "\n".join(f"<li>{d}</li>" for d in key_decisions)

        # 액션 아이템
        action_items_html = "\n".join(
            f'<tr>'
            f'<td style="border: 1px solid #333; padding: 8px;">{item["owner"]}</td>'
            f'<td style="border: 1px solid #333; padding: 8px;">{item["task"]}</td>'
            f'<td style="border: 1px solid #333; padding: 8px;">{item["due_date"]}</td>'
            f'</tr>'
            for item in action_items
        )

        # 작성자
        author_str = f'{info["author"]["name"]}/{info["author"]["position"]}/{info["author"]["email"]}'

        # 제목(작성자 이름 사용)
        title = info["title"]

        # 최종 HTML 생성
        html_result = html_template.format(
            title=title,
            date=info["date"],
            author=author_str,
            attendees=attendees_html,
            objectives=objectives_html,
            discussions=discussions_html,
            decisions=decisions_html,
            action_items=action_items_html
        )

        # print(html_result)
        return html_result
