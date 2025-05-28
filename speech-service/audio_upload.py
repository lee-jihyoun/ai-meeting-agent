import os
import time

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from datetime import datetime

load_dotenv()


# # # [Step 1] 특정 경로의 .wav 파일만 리스트로 가져오기
def get_wav_list():
    # 사용자의 홈 디렉터리 경로 얻기
    home_dir = os.path.expanduser('~')

    # Downloads 폴더 경로
    downloads_dir = os.path.join(home_dir, 'Downloads')

    # Downloads 폴더에서 .wav 파일만 리스트로 가져오기
    while True:
        audio_files = [f for f in os.listdir(downloads_dir) if f.lower().endswith('.wav') and f.lower().startswith('plamingo_meeting')]
        if audio_files:
            return audio_files, downloads_dir
        else:
            print('.wav 파일이 존재하지 않습니다. 10초 뒤에 다시 탐색합니다.')
            time.sleep(10)


# # # [Step 2] audio 파일을 blob storage에 업로드하기
def upload_audio_to_blob(audio_files, downloads_dir, container_name):
    # Azure Storage 연결 문자열과 컨테이너 이름
    connection_string = os.getenv("BLOB_CONNECTION_STRING")
    # container_name = "meeting-audio"
    # BlobServiceClient 생성
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # 파일 업로드
    for audio in audio_files:
        filename, ext = os.path.splitext(audio)
        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{start_time}] {audio} 파일을 blob storage에 업로드합니다.")
        # Blob에 저장될 파일 이름
        blob_audio_name = f"{filename}.wav"
        # 컨테이너의 BlobClient 생성
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_audio_name)
        with open(f"{downloads_dir}/{audio}", "rb") as data:
            blob_client.upload_blob(data, overwrite=True) # 덮어쓰기 허용
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{end_time}] {audio} 파일이 {container_name} 컨테이너에 업로드되었습니다.")