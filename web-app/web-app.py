from flask import Flask, render_template, request, jsonify, json
from urllib.parse import urlencode
import requests

app = Flask(__name__)

# TODO: .env 에서 받아오는 방식으로 수정 필요
# LOGIC_APP_URL = "https://prod-31.koreacentral.logic.azure.com:443/workflows/564e525201dc46d4b16939bf8a4aa104/triggers/manual/invoke"  # <- 여기에 실제 Logic App URL 입력!
LOGIC_APP_URL = "https://prod-31.koreacentral.logic.azure.com:443/workflows/564e525201dc46d4b16939bf8a4aa104"  # <- 여기에 실제 Logic App URL 입력!
# api-version 쿼리 파라미터 추가
params = {"api-version": "2025-06-01-preview"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api', methods=['POST'])
def api_endpoint():
    # 외부 API 로부터 오는 데이터 처리 예시
    data = request.get_json()
    # data = request.form # POST 요청에서 form 데이터 추출

    print("Received in /api:", data)  # 디버깅: 수신된 데이터 출력

    # 예시로 받은 데이터를 그대로 반환
    return jsonify(data) # data를 JSON 형식으로 응답
    # return jsonify(response)


@app.route('/start_meeting', methods=['POST'])
def start_meeting():

    hidden_value = request.form.get('hiddenValue')
    writer_name = request.form.get('writerName')
    date = request.form.get('date')

     # 디버깅을 위한 출력
    print(f"Received data - hidden_value:", {hidden_value}, "writer_name:", {writer_name}, "date:", {date})

    external_url = "http://localhost:5000/api" # 외부 API URL 예시

    external_data = {
        'hiddenValue': hidden_value,
        'writerName': writer_name,
        'date': date
    }

    try:    
        json_string = json.dumps(external_data, ensure_ascii=False).encode('utf-8')
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'text/plain'}

        print("Received in /start_meeting:", json_string)

        external_response  = requests.post(external_url, json=external_data, headers=headers)

        print(f"Received after external_response:", {external_response.text})

        # JSON 형식으로 응답 변환
        # return jsonify(response.json()) # 응답 반환

        print(f"[응답] 상태코드 : {external_response.status_code}, 본문 : {external_response.text}")
        if external_response.status_code == 200:
            # 성공적으로 응답을 받았을 경우
            response_data = json.loads(external_response.text)
            return jsonify(response_data)
        
        else:
            # 오류 발생 시
            return jsonify({'error': 'Error calling external API'}), 500        
    except Exception as e:
        # TODO 상용 배포일 경우, 추후 print문 제거 필요
        print(f"[오류] {str(e)}")

        return jsonify({"message": f"오류 발생: {str(e)}"}), 500

# TODO: 아래 코드 반드시 필요한지 확인할것 (chatGPT 답변 참고)    
if __name__ == '__main__':
    app.run(debug=True)    