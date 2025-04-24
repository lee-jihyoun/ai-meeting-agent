# 요약 처리 및 이메일 발송 관련 함수 임포트
from summary_service.summarize_meeting import summarize_meeting
from summary_service.email_sender import send_summary_email
from image_service.analyze_and_summarize import analyze_document, summarize_result, save_summary

# Flask 웹 서버 관련 모듈
from flask import Flask, render_template, request, jsonify

# 외부 API 호출용 모듈
import requests
import subprocess
import threading

# Flask 애플리케이션 인스턴스 생성
app = Flask(__name__)

# 가장 최신 요약 결과를 저장할 전역 변수
latest_summary = ""

# TODO: .env 에서 받아오는 방식으로 수정 필요
LOGIC_APP_URL = "https://your-logicapp-url.com/..."  # 실제 Logic App HTTP 트리거 URL로 변경해야 함

# 루트 경로 접근 시 index.html 렌더링
@app.route('/')
def index():
    return render_template('index.html')

# "회의 시작" 버튼 클릭 시 실행되는 라우트
@app.route('/start_meeting', methods=['POST'])
def start_meeting():
    try:
        # Logic App에 회의 시작 신호 전송
        logic_res = requests.post(LOGIC_APP_URL, json={"event": "meeting_started"})
        
        # 응답이 실패일 경우, 클라이언트에 오류 메시지 전송
        if logic_res.status_code != 200:
            return jsonify({
                "message": "⚠️ Logic App 호출 실패",
                "logic_status": logic_res.status_code
            }), 502

        # STT 클라이언트 subprocess를 별도 쓰레드에서 실행
        def run_audio_client():
            # client_audio_stream.py 호출
            result = subprocess.call(["python", "speech-service/client_audio_stream.py"])
            if result != 0:
                print(f"STT client exit code: {result}")

        # 이미지 캡처 루프 subprocess 실행
        def run_image_loop():
            subprocess.call(["python", "image_capture_loop.py"])

        # 오디오 및 이미지 수집 쓰레드 시작
        threading.Thread(target=run_audio_client).start()
        threading.Thread(target=run_image_loop).start()

        return jsonify({"message": "🎧 음성 및 이미지 캡처가 시작되었습니다!"}), 200

    except Exception as e:
        # 예외 발생 시 오류 정보와 함께 클라이언트에 반환
        return jsonify({
            "message": "⚠️ 예기치 않은 오류 발생",
            "error": str(e)
        }), 500

# 최신 요약 결과를 반환하는 API (웹페이지에서 실시간 표시용)
@app.route('/get_summary')
def get_summary():
    return jsonify({"summary": latest_summary})

# TODO 이메일 보낼 대상도 .env 에서 관리하도록 처리 필요
# POST로 들어온 파일을 요약하고 이메일로 발송하는 API
@app.route('/run_summary', methods=['POST'])
def run_summary():
    global latest_summary
    filename = request.json.get("filename") # 요청으로부터 분석할 파일명 추출
    latest_summary = summarize_meeting(filename) # 요약 처리
    send_summary_email(latest_summary, ["example@domain.com"]) # 이메일 발송
    return jsonify({"message": "요약 및 이메일 발송 완료!"})

# Logic App에서 이미지를 Blob Storage에 업로드한 후, 그 업로드된 이미지 URL(blob_url)을 서버에 알려줄 때 호출하는 엔드포인트
@app.route("/document_uploaded", methods=["POST"])
def handle_uploaded_document():
    """
    Logic App에서 이미지 업로드 후 호출하는 API (blob_url 전달됨)
    """
    global latest_summary
    try:
        blob_url = request.json.get("blob_url")
        if not blob_url:
            return jsonify({"error": "blob_url이 없습니다"}), 400

        print(f"📥 업로드 이미지 수신: {blob_url}")
        result = analyze_document(blob_url)
        summary = summarize_result(result)

        # 파일 저장
        save_summary(summary)

        # 실시간용 변수 저장
        latest_summary = summary

        # 이메일 발송
        send_summary_email(summary, ["example@domain.com"])

        return jsonify({"message": "요약 완료 및 저장/발송 성공", "summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# TODO: 아래 코드 반드시 필요한지 확인할것 (chatGPT 답변 참고) 
# 이 스크립트가 메인으로 실행될 때만 서버 실행
# (다른 파일에서 import되는 경우 실행되지 않도록 하기 위함)   
if __name__ == '__main__':
    app.run(debug=True) # 디버그 모드로 Flask 실행
