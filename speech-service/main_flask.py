from flask import Flask, request, jsonify
import os
import shutil
import json

from audio_upload import get_wav_list, upload_audio_to_blob
from generate_sas_url import generate_sas
from batch_transcription_api import req_batch_transcription_api, save_response_to_json, save_to_text, upload_txt_to_blob

app = Flask(__name__)

# 0. 변수 정의
container_name = "meeting-audio"


@app.route('/transcribe', methods=['POST'])
def transcribe():
    info = request.form.get('info')
    if not info:
        return jsonify({'error': 'info is required'}), 400

    # 1. 음성 파일을 blob 업로드
    audio_files, downloads_dir = get_wav_list()
    upload_audio_to_blob(audio_files, downloads_dir, container_name)

    # 2. sas url 생성
    for audio in audio_files:
        sas_url = generate_sas(container_name, audio)

        # 3. batch_transcription_api를 사용하여 음성파일을 txt로 변환
        response_json = req_batch_transcription_api(sas_url)
        today_str, output_dir = save_response_to_json(response_json)
        save_to_text(output_dir)

        # 4. txt 파일을 blob 업로드
        upload_txt_to_blob(today_str, output_dir, info)

    return jsonify({'status': 'success', 'info': info}), 200


if __name__ == '__main__':
    app.run(debug=True)

# TODO: flask로 api 개발.
# response를 주지 않고, blob에 txt와 info json 또는 txt 로 같이 올리기.
