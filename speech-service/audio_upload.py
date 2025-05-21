import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from datetime import datetime

load_dotenv()

# # # [Step 1] 특정 경로의 .wav 파일만 리스트로 가져오기
# 사용자의 홈 디렉터리 경로 얻기
home_dir = os.path.expanduser('~')

# Downloads 폴더 경로 만들기
downloads_dir = os.path.join(home_dir, 'Downloads')

# Downloads 폴더에서 .wav 파일만 리스트로 가져오기
audio_files = [f for f in os.listdir(downloads_dir) if f.lower().endswith('.wav')]
# print(audio_files)

# 오늘 날짜를 YYYY-MM-DD 형식으로 문자열 생성
# today_str = datetime.now().strftime("%Y-%m-%d")


# # # [Step 2] audio 파일을 blob storage에 업로드하기
# Azure Storage 연결 문자열과 컨테이너 이름
connection_string = os.getenv("BLOB_CONNECTION_STRING")
container_name = "meeting-audio"

# BlobServiceClient 생성
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

# 파일 업로드
for audio in audio_files:
    filename, ext = os.path.splitext(audio)
    print(f"{audio} 파일을 blob storage에 업로드합니다.")
    # Blob에 저장될 파일 이름
    blob_audio_name = f"{filename}.wav"
    # 컨테이너의 BlobClient 생성
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_audio_name)
    with open(f"{downloads_dir}/{audio}", "rb") as data:
        blob_client.upload_blob(data, overwrite=True) # 덮어쓰기 허용
    print(f"'{audio}' 파일이 '{container_name}' 컨테이너에 '{blob_audio_name}' 이름으로 업로드되었습니다.")