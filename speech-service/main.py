from audio_upload import get_wav_list, upload_audio_to_blob
from generate_sas_url import generate_sas
from batch_transcription_api import req_batch_transcription_api, save_response_to_json, save_to_text, upload_txt_to_blob
import sys

# 0. 변수 정의
container_name = "meeting-audio"
info = {"이름": "홍길동"}

# 1. 음성 파일을 blob 업로드
audio_files, downloads_dir = get_wav_list()
upload_audio_to_blob(audio_files, downloads_dir, container_name)

# 2. sas url 생성
for audio in audio_files:
    sas_url = generate_sas(container_name, audio)

    # 3. batch_transcription_api를 사용하여 음성파일을 txt로 변환
    response_json = req_batch_transcription_api(sas_url)

    try:
        today_str, output_dir = save_response_to_json(response_json)
    except Exception as e:
        print(e)
        sys.exit()

    save_to_text(output_dir)

    # 4. txt 파일을 blob 업로드
    upload_txt_to_blob(today_str, output_dir, info)


# TODO: flask로 api 개발.
# reqest: info json 안에 프론트에서 받는 모든 값이 포함되어 있어야 함.
# main.py api의 역할은 .wav를 .txt로 변환하는 것
# response를 주지 않고, blob에 txt와 info json 또는 txt 로 같이 올리기.
