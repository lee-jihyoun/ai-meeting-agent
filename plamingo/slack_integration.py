"""
Slack Integration using MCP (Model Context Protocol)
Logic Apps에서 발송하는 메일 내용을 Slack 채널에 전송
"""

import os
import json
import subprocess
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class SlackMCPClient:
    """MCP Slack 서버를 사용하는 클라이언트"""

    def __init__(self):
        self.bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.team_id = os.getenv("SLACK_TEAM_ID")
        self.channel_id = os.getenv("SLACK_CHANNEL_ID")

        if not all([self.bot_token, self.team_id, self.channel_id]):
            raise ValueError("Slack 환경변수가 설정되지 않았습니다.")

    def send_message(self, text: str) -> dict:
        """
        Slack 채널에 메시지 전송

        Args:
            text: 전송할 메시지 내용

        Returns:
            응답 결과 딕셔너리
        """
        try:
            # MCP Slack 서버를 통해 메시지 전송
            # stdio 모드로 MCP 서버 호출
            env = os.environ.copy()
            env['SLACK_BOT_TOKEN'] = self.bot_token
            env['SLACK_TEAM_ID'] = self.team_id

            # MCP 요청 페이로드
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "slack_post_message",
                    "arguments": {
                        "channel_id": self.channel_id,
                        "text": text
                    }
                }
            }

            # node_modules의 MCP Slack 서버 실행 (절대 경로)
            mcp_server_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "node_modules/@zencoderai/slack-mcp-server/dist/index.js"
            )

            process = subprocess.Popen(
                ['node', mcp_server_path, '--transport', 'stdio'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )

            # MCP 요청 전송
            print(f"🚀 MCP 서버 경로: {mcp_server_path}")
            print(f"📤 MCP 요청: {json.dumps(mcp_request, ensure_ascii=False)[:150]}")

            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request) + '\n',
                timeout=10
            )

            print(f"📥 MCP stdout 길이: {len(stdout)}, stderr 길이: {len(stderr)}")

            if stderr:
                print(f"⚠️ MCP 서버 stderr: {stderr[:300]}")

            if stdout:
                print(f"📄 MCP stdout: {stdout[:300]}")

            # 응답 파싱 (JSON 라인만 추출)
            lines = stdout.strip().split('\n')
            json_lines = [line for line in lines if line.strip().startswith('{')]

            if not json_lines:
                raise Exception(f"MCP 서버 응답에 JSON이 없습니다.\nstdout: {stdout[:500]}\nstderr: {stderr[:500]}")

            response = json.loads(json_lines[-1])

            if 'error' in response:
                raise Exception(f"MCP 에러: {response['error']}")

            return {
                'success': True,
                'response': response.get('result', {})
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'MCP 서버 응답 시간 초과'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def format_meeting_email_message(self, email_data: dict) -> str:
        """
        Logic Apps에서 발송하는 이메일 내용을 Slack 메시지 형식으로 변환

        Args:
            email_data: 이메일 데이터 (제목, 내용, 수신자 등)

        Returns:
            포맷된 Slack 메시지
        """
        message_parts = []

        # 헤더
        message_parts.append("📧 *회의록 메일 발송*")
        message_parts.append("")

        # 제목
        if 'subject' in email_data:
            message_parts.append(f"*제목:* {email_data['subject']}")

        # 수신자
        if 'to' in email_data:
            recipients = email_data['to']
            if isinstance(recipients, list):
                recipients = ', '.join(recipients)
            message_parts.append(f"*수신자:* {recipients}")

        # 내용 미리보기
        if 'body' in email_data:
            body = email_data['body']
            # HTML 태그 제거 (간단한 처리)
            if '<html>' in body.lower():
                # HTML 본문인 경우 간단하게 요약
                message_parts.append("")
                message_parts.append("*내용:*")
                message_parts.append("회의록이 이메일로 발송되었습니다.")
            else:
                # 텍스트 본문인 경우
                preview = body[:200] + "..." if len(body) > 200 else body
                message_parts.append("")
                message_parts.append("*내용:*")
                message_parts.append(f"```{preview}```")

        # 링크 (있는 경우)
        if 'link' in email_data:
            message_parts.append("")
            message_parts.append(f"🔗 <{email_data['link']}|회의록 보기>")

        # 타임스탬프
        if 'timestamp' in email_data:
            message_parts.append("")
            message_parts.append(f"_발송 시각: {email_data['timestamp']}_")

        return '\n'.join(message_parts)


def send_meeting_email_notification(email_data: dict) -> dict:
    """
    회의록 이메일 발송 알림을 Slack으로 전송

    Args:
        email_data: Logic Apps에서 전달받은 이메일 데이터

    Returns:
        전송 결과
    """
    try:
        client = SlackMCPClient()
        message = client.format_meeting_email_message(email_data)
        result = client.send_message(message)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_meeting_notes_notification(meeting_info: dict, file_name: str, meeting_notes_url: str) -> dict:
    """
    회의록 생성 완료 알림을 Slack으로 전송

    Args:
        meeting_info: 회의 정보 (title, writer, attendees, startTime, content 등)
        file_name: 생성된 파일명
        meeting_notes_url: 회의록 URL

    Returns:
        전송 결과
    """
    try:
        client = SlackMCPClient()

        # 참석자 이름 리스트 생성
        attendee_names = [a.get('name', '') for a in meeting_info.get('attendees', [])]
        attendee_text = ', '.join(attendee_names) if attendee_names else "정보 없음"

        # 작성자 정보
        writer = meeting_info.get('writer', ['정보 없음', '', ''])
        writer_name = writer[0] if len(writer) > 0 else "정보 없음"
        writer_position = writer[1] if len(writer) > 1 else ""
        writer_info = f"{writer_name} ({writer_position})" if writer_position else writer_name

        # Slack 메시지 구성
        message_parts = []
        message_parts.append("📝 *회의록이 생성되었습니다*")
        message_parts.append("")
        message_parts.append(f"*회의 제목:* {meeting_info.get('title', '제목 없음')}")
        message_parts.append(f"*작성자:* {writer_info}")
        message_parts.append(f"*시작 시간:* {meeting_info.get('startTime', '정보 없음')}")
        message_parts.append(f"*참석자:* {attendee_text}")
        message_parts.append("")
        message_parts.append(f"*회의 내용:*")
        message_parts.append(f"{meeting_info.get('content', '내용 없음')}")
        message_parts.append("")
        message_parts.append(f"🔗 <{meeting_notes_url}|회의록 보기>")

        message = '\n'.join(message_parts)
        result = client.send_message(message)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # 테스트
    test_email_data = {
        'subject': '회의록: 2025년 12월 프로젝트 킥오프 미팅',
        'to': 'team@example.com',
        'body': '안녕하세요. 회의록을 첨부합니다.',
        'timestamp': '2025-12-02 14:30:00'
    }

    result = send_meeting_email_notification(test_email_data)
    print(json.dumps(result, indent=2, ensure_ascii=False))
