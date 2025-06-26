import os
import time

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

# 현재 파일 기준으로 .env의 절대경로 생성
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path)

account_name = "staz01plamingo01"
account_key = os.getenv("STORAGE_ACCESS_KEY")


# # # [Step 1] 특정 경로의 .wav 파일만 리스트로 가져오기
# def get_wav_list():
#     # 사용자의 홈 디렉터리 경로 얻기
#     home_dir = os.path.expanduser('~')
#
#     # Downloads 폴더 경로
#     downloads_dir = os.path.join(home_dir, 'Downloads')
#
#     # Downloads 폴더에서 .wav 파일만 리스트로 가져오기
#     while True:
#         audio_files = [f for f in os.listdir(downloads_dir) if f.lower().endswith('.wav') and f.lower().startswith('plamingo_meeting')]
#         if audio_files:
#             return audio_files, downloads_dir
#         else:
#             print('.wav 파일이 존재하지 않습니다. 10초 뒤에 다시 탐색합니다.')
#             time.sleep(10)


# 파일을 blob storage에 업로드하기
def upload_to_blob(file_name, meeting_notes, container_name, email):

    # Azure Storage 연결 문자열과 컨테이너 이름
    connection_string = os.getenv("BLOB_CONNECTION_STRING")
    # BlobServiceClient 생성
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    # 컨테이너의 BlobClient 생성
    # # blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{email}.html")
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"{file_name}.html")

    blob_client.upload_blob(meeting_notes, overwrite=True) # 덮어쓰기 허용
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{end_time}] {file_name}.html 파일이 {container_name} 컨테이너에 업로드되었습니다.")


# def download_audio_from_blob(container_name, blob_name, download_file_path):
#     connection_string = os.getenv("BLOB_CONNECTION_STRING")
#     blob_service_client = BlobServiceClient.from_connection_string(connection_string)
#     # BlobClient 생성
#     blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
#
#     # WAV 파일 다운로드
#     with open(download_file_path, "wb") as file:
#         download_stream = blob_client.download_blob()
#         file.write(download_stream.readall())
#
#     print(f"WAV 파일이 {download_file_path}로 다운로드되었습니다.")



