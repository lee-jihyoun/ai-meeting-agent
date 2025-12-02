"""
Google Calendar Integration (서비스 계정 방식 - 간단함)
회의록에서 다음 회의 일정을 추출하여 구글 캘린더에 저장
"""

import os
import json
import re
from typing import Dict
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()


class GoogleCalendarClient:
    """구글 캘린더 클라이언트 (서비스 계정 사용)"""

    def __init__(self):
        """서비스 계정으로 인증"""
        credentials_file = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE")

        if not credentials_file:
            raise ValueError("GOOGLE_CALENDAR_CREDENTIALS_FILE 환경변수가 설정되지 않았습니다.")

        if not os.path.exists(credentials_file):
            raise ValueError(f"서비스 계정 파일을 찾을 수 없습니다: {credentials_file}")

        try:
            # 서비스 계정 인증
            SCOPES = ['https://www.googleapis.com/auth/calendar']
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file, scopes=SCOPES
            )

            # Calendar API 서비스 생성
            self.service = build('calendar', 'v3', credentials=credentials)
            self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")

            print("✅ 구글 캘린더 인증 완료")

        except Exception as e:
            raise ValueError(f"구글 캘린더 인증 오류: {e}")

    def create_event(self, event_data: Dict) -> Dict:
        """
        구글 캘린더에 이벤트 생성

        Args:
            event_data: 이벤트 정보
                {
                    "summary": "회의 제목",
                    "description": "회의 설명",
                    "start": "2025-12-10T14:00:00",
                    "end": "2025-12-10T15:00:00"
                }

        Returns:
            생성된 이벤트 정보
        """
        try:
            # 이벤트 객체 구성
            event = {
                'summary': event_data.get('summary', '회의'),
                'description': event_data.get('description', ''),
                'start': {
                    'dateTime': event_data.get('start'),
                    'timeZone': 'Asia/Seoul',
                },
                'end': {
                    'dateTime': event_data.get('end'),
                    'timeZone': 'Asia/Seoul',
                },
            }

            # API로 전송되는 body 데이터 로그 출력
            print("=" * 80)
            print("🔍 구글 캘린더 API로 전송되는 body 데이터:")
            print(f"  calendarId: {self.calendar_id}")
            print(f"  event body: {json.dumps(event, indent=2, ensure_ascii=False)}")
            print("=" * 80)

            # 캘린더에 이벤트 생성
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()

            print(f"✅ 캘린더 이벤트 생성 완료: {created_event.get('htmlLink')}")

            return {
                'success': True,
                'event_id': created_event.get('id'),
                'event_link': created_event.get('htmlLink'),
                'event': created_event
            }

        except HttpError as error:
            print(f"❌ 캘린더 이벤트 생성 실패: {error}")
            return {
                'success': False,
                'error': str(error)
            }


def parse_next_meeting_from_notes(meeting_json: Dict) -> Dict:
    """
    회의록 JSON에서 다음 회의 일정 정보 추출

    Args:
        meeting_json: 회의록 JSON 데이터

    Returns:
        다음 회의 정보
    """
    try:
        # Action Items에서 다음 회의 일정 찾기
        action_items = meeting_json.get('minutes', {}).get('action_items', [])

        next_meeting_info = None

        for item in action_items:
            task = item.get('task', '').lower()
            # "다음 회의", "차기 회의", "후속 회의" 등의 키워드 확인
            if any(keyword in task for keyword in ['다음 회의', '차기 회의', '후속 회의', 'next meeting']):
                next_meeting_info = item
                break

        # 또는 결정사항에서 다음 회의 일정 찾기
        if not next_meeting_info:
            key_decisions = meeting_json.get('minutes', {}).get('key_decisions', [])
            for decision in key_decisions:
                decision_lower = decision.lower()
                if any(keyword in decision_lower for keyword in ['다음 회의', '차기 회의', '후속 회의', 'next meeting']):
                    next_meeting_info = {
                        'task': decision,
                        'due_date': extract_date_from_text(decision)
                    }
                    break

        if next_meeting_info:
            return {
                'found': True,
                'task': next_meeting_info.get('task', ''),
                'due_date': next_meeting_info.get('due_date', ''),
                'owner': next_meeting_info.get('owner', '')
            }

        return {'found': False}

    except Exception as e:
        print(f"⚠️ 다음 회의 일정 파싱 중 오류: {e}")
        return {'found': False}


def extract_date_from_text(text: str) -> str:
    """텍스트에서 날짜 정보 추출 (YYYY-MM-DD)"""
    # YYYY-MM-DD 패턴
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    match = re.search(date_pattern, text)
    if match:
        return match.group()

    # YYYY년 MM월 DD일 패턴
    korean_date_pattern = r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일'
    match = re.search(korean_date_pattern, text)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    return ""


def create_calendar_event_from_meeting(meeting_json: Dict, meeting_info: Dict) -> Dict:
    """
    회의록에서 추출한 다음 회의 일정을 구글 캘린더에 저장

    Args:
        meeting_json: 회의록 JSON 데이터
        meeting_info: 원본 회의 정보

    Returns:
        캘린더 이벤트 생성 결과
    """
    try:
        # 다음 회의 정보 추출
        next_meeting = parse_next_meeting_from_notes(meeting_json)

        if not next_meeting.get('found'):
            return {
                'success': False,
                'message': '회의록에서 다음 회의 일정을 찾을 수 없습니다.'
            }

        # 날짜 정보가 없으면 스킵
        if not next_meeting.get('due_date'):
            return {
                'success': False,
                'message': '다음 회의 날짜 정보가 없습니다.'
            }

        # 구글 캘린더 클라이언트 초기화
        calendar_client = GoogleCalendarClient()

        # 시작/종료 시간 구성
        start_datetime = f"{next_meeting['due_date']}T10:00:00"
        end_datetime = f"{next_meeting['due_date']}T11:00:00"

        # 이벤트 제목 구성
        original_title = meeting_json.get('minutes', {}).get('info', {}).get('title', '회의')
        event_title = f"{original_title} - 후속 회의"

        # 이벤트 데이터 구성
        event_data = {
            'summary': event_title,
            'description': f"다음 회의 안건: {next_meeting['task']}",
            'start': start_datetime,
            'end': end_datetime
        }

        # 캘린더 이벤트 생성
        result = calendar_client.create_event(event_data)

        return result

    except Exception as e:
        print(f"❌ 캘린더 이벤트 생성 중 오류: {e}")
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # 테스트
    test_meeting_json = {
        "minutes": {
            "info": {
                "title": "프로젝트 킥오프 미팅"
            },
            "action_items": [
                {
                    "owner": "홍길동",
                    "task": "다음 회의 일정 조율",
                    "due_date": "2025-12-10"
                }
            ]
        }
    }

    test_meeting_info = {}

    result = create_calendar_event_from_meeting(test_meeting_json, test_meeting_info)
    print(json.dumps(result, indent=2, ensure_ascii=False))
