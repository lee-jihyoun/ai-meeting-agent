from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    data = request.get_json()

    if not data or "action" not in data:
        return jsonify({"error": "Missing action parameter"}), 400

    action = data.get("action")
    email = data.get("email")

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
