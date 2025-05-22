import os

from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# 필수 정보
account_name = "staz01plamingo01"
account_key = os.getenv("STORAGE_ACCESS_KEY")
# container_name = "meeting-audio"
# blob_file_name = "2025-05-21_meeting.wav"


def generate_sas(container_name, blob_file_name):
    # SAS 토큰 유효 기간 설정 (예: 1시간)
    sas_token_expiry = datetime.utcnow() + timedelta(hours=24)

    # SAS 토큰 생성
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=blob_file_name,
        account_key=account_key,
        permission=BlobSasPermissions(read=True, list=True),
        expiry=datetime.utcnow() + timedelta(hours=24),
        start=datetime.utcnow() - timedelta(minutes=15),  # 시작 시간 15분 전
        version="2022-11-02"  # 서비스 버전 명시
    )

    # Blob URL + SAS 토큰 조합하여 SAS URL 생성
    blob_url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_file_name}"
    print(blob_url)
    sas_url = f"{blob_url}?{sas_token}"
    print("SAS URL:", sas_url)
    return blob_url, sas_url
