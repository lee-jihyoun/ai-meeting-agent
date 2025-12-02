"""
Slack MCP를 이용한 회의록 알림 전송 모듈
진짜 MCP (Model Context Protocol) 사용
"""
import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()


class SlackMCPNotifier:
    def __init__(self):
        self.slack_channel = os.getenv("SLACK_CHANNEL", "#general")
        self.mcp_server_command = os.getenv("SLACK_MCP_SERVER_COMMAND", "npx")
        self.mcp_server_args = os.getenv("SLACK_MCP_SERVER_ARGS", "-y @modelcontextprotocol/server-slack").split()
        self.slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_team_id = os.getenv("SLACK_TEAM_ID")

        if not self.slack_bot_token:
            print("⚠️ SLACK_BOT_TOKEN이 설정되지 않았습니다.")

        if not self.slack_team_id:
            print("⚠️ SLACK_TEAM_ID가 설정되지 않았습니다.")

    async def _send_slack_message_via_mcp(self, channel, message):
        """MCP를 통해 Slack 메시지 전송"""
        try:
            server_params = StdioServerParameters(
                command=self.mcp_server_command,
                args=self.mcp_server_args,
                env={
                    "SLACK_BOT_TOKEN": self.slack_bot_token,
                    "SLACK_TEAM_ID": self.slack_team_id
                }
            )

            # stdio_client와 session을 context manager로 사용
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    print("✅ MCP Slack Server 연결 완료")

                    # 사용 가능한 툴 목록 확인
                    tools = await session.list_tools()
                    print(f"🔍 사용 가능한 MCP 툴: {[tool.name for tool in tools.tools]}")

                    # MCP의 slack_post_message 툴 호출 (올바른 툴 이름 사용)
                    result = await session.call_tool(
                        "slack_post_message",
                        arguments={
                            "channel_id": channel,
                            "text": message
                        }
                    )

                    print(f"✅ MCP를 통한 Slack 메시지 전송 완료: {result}")
                    return True

        except Exception as e:
            print(f"❌ MCP 메시지 전송 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

    def send_meeting_notification(self, meeting_info, file_name, meeting_notes_url):
        """
        회의록 생성 완료 알림을 Slack으로 전송 (MCP 사용)

        Args:
            meeting_info: 회의 정보 (title, writer, attendees, startTime 등)
            file_name: 파일명
            meeting_notes_url: 회의록 URL
        """
        if not self.slack_bot_token or not self.slack_team_id:
            print("⚠️ Slack 환경 변수가 설정되지 않았습니다.")
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

            # 메시지 구성
            message = f"""📝 *회의록이 생성되었습니다*

*회의 제목:* {meeting_info.get('title', '제목 없음')}
*작성자:* {writer_info}
*시작 시간:* {meeting_info.get('startTime', '정보 없음')}
*참석자:* {attendee_text}

*회의 내용:*
{meeting_info.get('content', '내용 없음')}

📄 회의록 보기: {meeting_notes_url}
"""

            # MCP를 통해 메시지 전송 (asyncio 사용)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._send_slack_message_via_mcp(self.slack_channel, message)
            )
            loop.close()

            return result

        except Exception as e:
            print(f"❌ Slack 알림 전송 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            return False

    def send_simple_message(self, message):
        """
        간단한 텍스트 메시지 전송 (MCP 사용)

        Args:
            message: 전송할 메시지
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self._send_slack_message_via_mcp(self.slack_channel, message)
            )
            loop.close()
            return result

        except Exception as e:
            print(f"❌ Slack 메시지 전송 실패: {e}")
            import traceback
            traceback.print_exc()
            return False


# 싱글톤 인스턴스 생성
slack_notifier = SlackMCPNotifier()
