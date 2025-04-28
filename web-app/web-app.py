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
    data = {
        "meetingId": "2025-04-22-회의",
        "startedBy": "홍길동"
    }
    # TODO 상용 배포일 경우, 추후 print문 제거 필요
    print(f"[요청] Logic App 에 전송 : {data}")

    try:
        response = requests.post(LOGIC_APP_URL, json=data)
        # TODO 상용 배포일 경우, 추후 print문 제거 필요
        print(f"[응답] 상태코드 : {response.status_code}, 본문 : {response.text}")

        if response.status_code == 200:
            return jsonify({"message": "회의가 성공적으로 시작되었습니다!"})
        else:
            return jsonify({"message": f"Logic App 호출 실패: {response.status_code}"}), 500
    except Exception as e:
        # TODO 상용 배포일 경우, 추후 print문 제거 필요
        print(f"[오류] {str(e)}")

        return jsonify({"message": f"오류 발생: {str(e)}"}), 500


# TODO: 아래 코드 반드시 필요한지 확인할것 (chatGPT 답변 참고)    
if __name__ == '__main__':
    app.run(debug=True)    