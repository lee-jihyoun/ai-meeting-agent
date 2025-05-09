from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

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

    # action 값에 따라 분기 처리
    if action == "startMeeting":
        return process_start_meeting(email, attendees)
    elif action == "endMeeting":
        return process_end_meeting(email)
    else:
        return jsonify({"error": "Invalid action type"}), 400

def process_start_meeting(email, attendees):
    return jsonify({"status": "startMeeting", "email": email, "attendees" : attendees})

def process_end_meeting(email):
    return jsonify({"status": "endMeeting", "email": email})

if __name__ == '__main__':
    app.run(debug=True)
