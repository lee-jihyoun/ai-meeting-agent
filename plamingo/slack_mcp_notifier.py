"""
Slack MCP를 이용한 회의록 알림 전송 모듈
"""
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()


class SlackMCPNotifier:
    def __init__(self):
        self.slack_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_channel = os.getenv("SLACK_CHANNEL", "#general")

        if not self.slack_token:
            print("⚠️ SLACK_BOT_TOKEN이 설정되지 않았습니다.")
            self.client = None
        else:
            self.client = WebClient(token=self.slack_token)

    def send_meeting_notification(self, meeting_info, file_name, meeting_notes_url):
        """
        회의록 생성 완료 알림을 Slack으로 전송

        Args:
            meeting_info: 회의 정보 (title, writer, attendees, startTime 등)
            file_name: 파일명
            meeting_notes_url: 회의록 URL
        """
        if not self.client:
            print("⚠️ Slack 클라이언트가 초기화되지 않았습니다. SLACK_BOT_TOKEN을 확인하세요.")
            return False

        try:
            # 참석자 이름 리스트 생성
            attendee_names = [a.get('name', '') for a in meeting_info.get('attendees', [])]
            attendee_text = ', '.join(attendee_names) if attendee_names else "정보 없음"

            # 작성자 정보
            writer = meeting_info.get('writer', ['정보 없음', '', ''])
            writer_name = writer[0] if len(writer) > 0 else "정보 없음"
            writer_position = writer[1] if len(writer) > 1 else ""
            writer_info = f"{writer_name} ({writer_position})" if writer_position else writer_name

            # Slack 메시지 구성 (Block Kit 사용)
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📝 회의록이 생성되었습니다",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*회의 제목:*\n{meeting_info.get('title', '제목 없음')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*작성자:*\n{writer_info}"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*시작 시간:*\n{meeting_info.get('startTime', '정보 없음')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*참석자:*\n{attendee_text}"
                        }
                    ]
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*회의 내용:*\n{meeting_info.get('content', '내용 없음')}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "📄 회의록 보기",
                                "emoji": True
                            },
                            "url": meeting_notes_url,
                            "style": "primary"
                        }
                    ]
                }
            ]

            # Slack 메시지 전송
            response = self.client.chat_postMessage(
                channel=self.slack_channel,
                text=f"회의록이 생성되었습니다: {meeting_info.get('title', '제목 없음')}",
                blocks=blocks
            )

            if response["ok"]:
                print(f"✅ Slack 알림 전송 완료: {meeting_info.get('title', '제목 없음')}")
                return True
            else:
                print(f"❌ Slack 알림 전송 실패: {response}")
                return False

        except SlackApiError as e:
            print(f"❌ Slack API 오류 발생: {e.response['error']}")
            return False
        except Exception as e:
            print(f"❌ Slack 알림 전송 중 오류 발생: {e}")
            return False

    def send_simple_message(self, message):
        """
        간단한 텍스트 메시지 전송

        Args:
            message: 전송할 메시지
        """
        if not self.client:
            print("⚠️ Slack 클라이언트가 초기화되지 않았습니다.")
            return False

        try:
            response = self.client.chat_postMessage(
                channel=self.slack_channel,
                text=message
            )
            return response["ok"]
        except SlackApiError as e:
            print(f"❌ Slack API 오류: {e.response['error']}")
            return False


# 싱글톤 인스턴스 생성
slack_notifier = SlackMCPNotifier()
