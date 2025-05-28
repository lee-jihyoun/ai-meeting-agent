from audio_upload import get_wav_list, upload_audio_to_blob
from generate_sas_url import generate_sas
from batch_transcription_api import req_batch_transcription_api, save_response_to_json, save_to_text, upload_txt_to_blob
import sys

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
