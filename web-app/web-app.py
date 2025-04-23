from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

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
        def run_stt():
            # client_audio_stream.py 호출
            result = subprocess.call(["python", "speech-service/client_audio_stream.py"])
            if result != 0:
                print(f"STT client exit code: {result}")

        threading.Thread(target=run_stt).start()

        return jsonify({"message": "🎧 회의 음성 수집이 시작되었습니다!"}), 200

    except Exception as e:
        return jsonify({
            "message": "⚠️ 예기치 않은 오류 발생",
            "error": str(e)
        }), 500


# TODO: 아래 코드 반드시 필요한지 확인할것 (chatGPT 답변 참고)    
if __name__ == '__main__':
    app.run(debug=True)    
