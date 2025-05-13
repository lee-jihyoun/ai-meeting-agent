from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# TODO: .env 에서 받아오는 방식으로 수정 필요
LOGIC_APP_URL = "https://prod-08.koreacentral.logic.azure.com:443/workflows/3d3954b8179e4085a98c49cba1922ca1/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=Wt0QxuwWN9wn3tspR80nslavA3KZtDzZVvI2JL5j_kM";

@app.route('/')
def index():
    return render_template('recording.html')

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    # 요청 데이터(JSON)를 가져옴
    data = request.get_json()

    # 예외 처리: 데이터가 없거나 "action"이 없을 경우 오류 반환
    if not data or "action" not in data:
        return jsonify({"error": "Missing action parameter"}), 400

    # action 값을 가져옴
    action = data.get("action")
    email = data.get("email")
    attendees = data.get("attendees")

    external_data = {
        'action': action,
        'email': email,
        'attendees': attendees
    }

    headers = {"Content-Type": "application/json"}

    try : 
        external_response = requests.post(LOGIC_APP_URL, json=external_data, headers=headers, verify=False)
    except requests.exceptions.RequestException as e:
        print("webhook_handler 웹 요청 중 오류 발생:", e)

    if external_response.status_code == 200:
        response_data = json.loads(external_response.text)
        # action 값에 따라 분기 처리
        if action == "startMeeting":
            return process_start_meeting(email, attendees)
        elif action == "endMeeting":
            return process_end_meeting(email)
        else:
            return jsonify({"error": "Invalid action type"}), 400
        
    return external_response.text    

def process_start_meeting(email, attendees):
    return jsonify({"status": "startMeeting", "email": email, "attendees" : attendees})

def process_end_meeting(email):
    return jsonify({"status": "endMeeting", "email": email})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9090')
