import os

from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# 필수 정보
account_name = "staz01plamingo01"
account_key = os.getenv("AI_SERVICE_KEY")
# container_name = "meeting-audio"
# blob_file_name = "2025-05-21_meeting.wav"


def generate_sas(container_name, blob_file_name):
    # SAS 토큰 유효 기간 설정 (예: 1시간)
    sas_token_expiry = datetime.utcnow() + timedelta(hours=1)

    # SAS 토큰 생성
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_file_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True, list=True),  # 읽기 권한만 부여
        expiry=datetime.utcnow() + timedelta(hours=1),
        start=datetime.utcnow() - timedelta(minutes=15)  # 시작 시간을 5분 전으로
    )

    # Blob URL + SAS 토큰 조합하여 SAS URL 생성
    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_file_name}"
    sas_url = f"{blob_url}?{sas_token}"
    print("SAS URL:", sas_url)
    return sas_url
