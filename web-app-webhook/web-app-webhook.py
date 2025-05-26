from flask import Flask, request, jsonify, render_template
import requests, os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
LOGIC_APP_URL = os.getenv("LOGIC_APP_URL")

@app.route('/')
def index():
    return render_template('recording.html')

@app.route('/webhook', methods=['POST'])
def webhook_handler():

    info = request.get_json(force=True)
    # 요청 데이터(JSON)를 가져옴
    data = request.get_json()
    print("webhook_handler data : ", data)

    # 예외 처리: 데이터가 없거나 "meetingAction"이 없을 경우 오류 반환
    if not data or "meetingAction" not in data:
        return jsonify({"error": "Missing meetingAction parameter"}), 400

    # meetingAction 값을 가져옴
    meetingAction = data["meetingAction"]
    title = data["title"]
    content = data["content"]
    # writerName = data["writerName"]
    # writerPosition = data["writerPosition"]
    # writerEmail = data["writerEmail"]
    writer = data["writer"]
    attendees = data["attendees"]    
    startTime = data["startTime"]

    external_data = {
        'meetingAction': meetingAction,
        'title' : title,
        'content' : content,
        'writer': writer,
        'attendees' : attendees,
        'startTime' : startTime,
    }

    print("webhook_handler external_data : ", external_data)

    headers = {"Content-Type": "application/json"}

    try : 
        external_response = requests.post(LOGIC_APP_URL, json=external_data, headers=headers, verify=False)
    except requests.exceptions.RequestException as e:
        print("webhook_handler 웹 요청 중 오류 발생:", e)

    if external_response.status_code == 200:
        response_data = external_response.json()
        # meetingAction 값에 따라 분기 처리
        if meetingAction == "startMeeting":
            return process_start_meeting(writer[2], attendees)
        elif meetingAction == "endMeeting":
            return process_end_meeting(writer[2])
        else:
            return jsonify({"error": "Invalid meetingAction type"}), 400
        
    # return external_response.text    
    return jsonify({
        "status: ": "ok",
        "info": info
    }), 200

def process_start_meeting(writer_email, attendees):
    return jsonify({"status": "startMeeting", "email": writer_email, "attendees" : attendees})

def process_end_meeting(writer_email):
    return jsonify({"status": "endMeeting", "email": writer_email})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9090')
