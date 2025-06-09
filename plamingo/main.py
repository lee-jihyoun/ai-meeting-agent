from flask import Flask, request, jsonify, render_template
import requests, os
from dotenv import load_dotenv
import sys
from transcribe_api.audio_upload import get_wav_list, upload_audio_to_blob, generate_sas
from transcribe_api.batch_transcription_api import req_batch_transcription_api, save_response_to_json, save_to_text, upload_txt_to_blob

app = Flask(__name__)
load_dotenv()
LOGIC_APP_URL = os.getenv("LOGIC_APP_URL")


@app.route('/transcribe', methods=['POST'])
def transcribe():
    # 0. 변수 정의
    container_name = "meeting-audio"
    info = {"이름": "홍길동"}

    # 1. 음성 파일을 blob 업로드
    audio_files, downloads_dir = get_wav_list()
    upload_audio_to_blob(audio_files, downloads_dir, container_name)

    # 2. sas url 생성
    for audio in audio_files:
        blob_url, sas_url = generate_sas(container_name, audio)

        # 3. batch_transcription_api를 사용하여 음성파일을 txt로 변환
        response_json = req_batch_transcription_api(blob_url, sas_url)

        try:
            today_str, output_dir = save_response_to_json(response_json)
        except Exception as e:
            print(e)
            sys.exit()

        save_to_text(output_dir)

        # 4. txt 파일을 blob 업로드
        upload_txt_to_blob(today_str, output_dir, info)


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

    headers = {"Content-Type": "application/json"}

    try:
        external_response = requests.post(LOGIC_APP_URL, json=info, headers=headers, verify=False)
        # transcribe

        if external_response.status_code == 200:
            return jsonify({
                "status: ": "ok"
            }), 200
        else:
            return jsonify({"error": "Invalid meetingAction type"}), 400
    except requests.exceptions.RequestException as e:
        print("webhook_handler 웹 요청 중 오류 발생:", e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='9090')
