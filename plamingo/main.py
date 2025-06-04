from flask import Flask, request, jsonify, render_template
import requests, os
from dotenv import load_dotenv
import sys
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from transcribe_api.batch_transcription_api import req_batch_transcription_api, save_response_to_json, save_to_text, upload_txt_to_blob

app = Flask(__name__)
load_dotenv()
LOGIC_APP_URL = os.getenv("LOGIC_APP_URL")
account_name = "staz01plamingo01"
account_key = os.getenv("STORAGE_ACCESS_KEY") #스토리지계정의 액세스 키1의 값


@app.route('/transcribe', methods=['POST'])
def transcribe():
    # 0. 변수 정의
    container_name = "meeting-audio"
    info = {"이름": "홍길동"}

    # 1. 음성 파일을 blob 업로드 -> 프론트에서 수행.
    # audio_files, downloads_dir = get_wav_list()
    # upload_audio_to_blob(audio_files, downloads_dir, container_name)

    # TODO: blob storage에서 audio 파일을 내려받기 -> 필요없음 . blob url만 있으면 됨.

    # 2. sas url 생성
    # for audio in audio_files:
    # blob_url, sas_url = generate_sas(container_name, audio)

    # 3. batch_transcription_api를 사용하여 음성파일을 txt로 변환
    AUDIO_BLOB_SAS_URL = "https://staz01plamingo01.blob.core.windows.net/meeting-audio/%ED%9A%8C%EC%9D%98%EC%9D%8C%EC%84%B1.wav?sp=rcw&st=2025-05-14T05:01:19Z&se=2025-08-31T13:01:19Z&sv=2024-11-04&sr=b&sig=afQRWzll9OIq%2FSX2vdvrDRy06YxemjTwgZbY7TT3ow4%3D"
    blob_url = os.getenv(AUDIO_BLOB_SAS_URL)
    response_json = req_batch_transcription_api(blob_url)

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


@app.route('/generate_sas_url', methods=['GET'])
def generate_sas():
    blob_file_name = request.args.get('filename')  # 쿼리스트링에서 filename 파라미터 추출
    if not blob_file_name:
        return jsonify({'error': 'filename is required'}), 400
    container_name = "meeting-audio"

    # SAS 토큰 생성
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_file_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True, write=True, create=True, list=True),
        expiry=datetime.now(timezone.utc) + timedelta(hours=24),
        start=datetime.now(timezone.utc) - timedelta(minutes=15),
        version="2025-05-05"  # 리전별 최신 지원 버전으로 지정
    )

    # Blob URL + SAS 토큰 조합하여 SAS URL 생성
    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{quote(blob_file_name)}"
    sas_url = f"{blob_url}?{sas_token}"
    print("SAS URL:", sas_url)
    return jsonify({'sas_url': sas_url})


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port='9090')
    app.run(host='0.0.0.0', port='443', ssl_context=('cert.pem', 'key.pem'))
