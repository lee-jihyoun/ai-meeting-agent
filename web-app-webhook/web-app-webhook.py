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

    # action 값에 따라 분기 처리
    if action == "subscribe":
        return process_subscription(email)
    elif action == "unsubscribe":
        return process_unsubscription(email)
    else:
        return jsonify({"error": "Invalid action type"}), 400

def process_subscription(email):
    return jsonify({"status": "Subscribed", "email": email})

def process_unsubscription(email):
    return jsonify({"status": "Unsubscribed", "email": email})

if __name__ == '__main__':
    app.run(debug=True)
