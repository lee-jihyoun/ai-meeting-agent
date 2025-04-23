from summary_service.summarize_meeting import summarize_meeting
from summary_service.email_sender import send_summary_email
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

latest_summary = ""

# TODO: .env 에서 받아오는 방식으로 수정 필요
LOGIC_APP_URL = "https://your-logicapp-url.com/..."  # <- 여기에 실제 Logic App URL 입력!

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_meeting', methods=['POST'])
def start_meeting():
    try:
        # Logic App에 회의 시작 신호 전송
        logic_res = requests.post(LOGIC_APP_URL, json={"event": "meeting_started"})
        
        if logic_res.status_code != 200:
            return jsonify({
                "message": "⚠️ Logic App 호출 실패",
                "logic_status": logic_res.status_code
            }), 502

        # STT subprocess 실행
        def run_audio_client():
            # client_audio_stream.py 호출
            result = subprocess.call(["python", "speech-service/client_audio_stream.py"])
            if result != 0:
                print(f"STT client exit code: {result}")

        def run_image_loop():
            subprocess.call(["python", "image_capture_loop.py"])

        threading.Thread(target=run_audio_client).start()
        threading.Thread(target=run_image_loop).start()

        return jsonify({"message": "🎧 음성 및 이미지 캡처가 시작되었습니다!"}), 200

    except Exception as e:
        return jsonify({
            "message": "⚠️ 예기치 않은 오류 발생",
            "error": str(e)
        }), 500

# Flask 서버에서 요약 결과를 전달한것을 받음
@app.route('/get_summary')
def get_summary():
    return jsonify({"summary": latest_summary})

# TODO 이메일 보낼 대상 .env 에서 관리하도록 처리 필요
# 요약된 내용을 이메일 발송
@app.route('/run_summary', methods=['POST'])
def run_summary():
    global latest_summary
    filename = request.json.get("filename")
    latest_summary = summarize_meeting(filename)
    send_summary_email(latest_summary, ["example@domain.com"])
    return jsonify({"message": "요약 및 이메일 발송 완료!"})


# TODO: 아래 코드 반드시 필요한지 확인할것 (chatGPT 답변 참고)    
if __name__ == '__main__':
    app.run(debug=True)    
