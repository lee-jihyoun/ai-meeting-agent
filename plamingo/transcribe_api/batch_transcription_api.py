import os
import requests
from dotenv import load_dotenv
import time
from datetime import datetime
import json
from azure.storage.blob import BlobServiceClient

# 현재 파일 기준으로 .env의 절대경로 생성
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path)

speech_key = os.getenv("AI_SERVICE_KEY")
region = os.getenv("AI_SERVICE_REGION")
endpoint = os.getenv("AI_BATCH_TRANSCRIPTION_ENDPOINT")

# Azure Storage 연결 문자열과 컨테이너 이름
connection_string = os.getenv("BLOB_CONNECTION_STRING")
container_name = "meeting-text"


# blob url 사용은 public 으로 열린 경우. sas_url은 sas를 통해서만 사용하는 경우
# # # [Step1] blob storage에 업로드된 음성 파일을 batch_transcription_api에 요청
def req_batch_transcription_api(sas_url):
    # 1. Azure Blob Storage URL에 업로드된 음성 파일의 SAS URL 필요

    # 2. 전사 요청 payload
    payload = {
        "displayName": "회의녹음_전사",
        "description": "회의 전사 작업",
        "locale": "ko-KR",
        "contentUrls": [sas_url], # sas_url로 blob storage에 있는 파일 접근 가능
        "locale": "ko-KR",
        "displayName": "My Transcription",
        "model": None,  # 커스텀 모델이 있으면 넣기
        "properties": {
            "punctuationMode": "DictatedAndAutomatic",
            "profanityFilterMode": "Masked",
            "diarizationEnabled": True  # 화자 구분. True일때 대사 중복으로 안들어감
        }
    }

    headers = {
        "Ocp-Apim-Subscription-Key": speech_key,
        "Content-Type": "application/json"
    }

    # 전사 요청을 보냄
    response = requests.post(endpoint, json=payload, headers=headers)
    print(response.status_code)
    response_json = response.json()
    print(response_json)
    return response_json


# # # [Step2] batch_transcription_api의 응답을 json 파일로 저장
def save_response_to_json(response_json):
    # transcriptionId를 응답에서 추출
    transcription_id = response_json.get("self").split("transcriptions/")[1]

    # 오늘 날짜의 디렉토리 생성
    # 오늘 날짜를 YYYY-MM-DD 형식으로 문자열 생성
    today_str = datetime.now().strftime("%Y-%m-%d")

    # output_test/2025-05-14 형식의 경로 생성
    output_dir = os.path.join("output", today_str)

    # 디렉토리 생성 (이미 존재해도 에러 발생하지 않음)
    os.makedirs(output_dir, exist_ok=True)

    if not transcription_id:
        print("전사 작업 ID를 가져올 수 없습니다.")
    else:
        # 상태 확인을 위한 엔드포인트
        status_endpoint = f"{endpoint}/{transcription_id}"

        headers = {
            "Ocp-Apim-Subscription-Key": speech_key
        }

        # 전사 작업 상태 확인
        while True:
            response = requests.get(status_endpoint, headers=headers)
            result = response.json()
            status = result.get("status")
            print("현재 상태:", status)

            if status in ["Succeeded", "Failed"]:
                print("최종 상태 도달:", status)
                if status == 'Failed':
                    raise RuntimeError("batch transcription api를 사용할 수 없습니다.")

                files_url = f"https://koreacentral.api.cognitive.microsoft.com/speechtotext/v3.1/transcriptions/{transcription_id}/files"

                response = requests.get(files_url, headers=headers)
                files_info = response.json()
                # print(files_info)

                content_urls = [item["links"]["contentUrl"] for item in files_info["values"]]

                # 결과 출력
                for idx, url in enumerate(content_urls):
                    # 파일명 구분 (contenturl_0.json, report.json)
                    file_name = f"transcription_{idx}.json" if "report" not in url else "transcription_report.json"

                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(f"{output_dir}/{file_name}", "wb") as f:
                            f.write(response.content)
                        print(f"다운로드 완료: {file_name}")

                    else:
                        print(f"다운로드 실패: {url}")

                break

            time.sleep(10)  # 10초마다 상태 확인

    time.sleep(10)
    return today_str, output_dir


# # # [Step3] json 파일에서 대사만 추출하여 파일로 저장
def save_to_text(output_dir):
    # transcription_0.json 파일 로드
    with open(f"{output_dir}/transcription_0.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    full_text = []

    # 각 구절(phrase)에서 텍스트 추출
    for phrase in data["recognizedPhrases"]:
        if phrase["recognitionStatus"] == "Success":
            for nbest in phrase["nBest"]:
                full_text.append(nbest["display"])  # display 필드 사용

    # 결과 저장
    meeting_transcript = "\n".join(full_text)
    with open(f"{output_dir}/meeting_transcript.txt", "w", encoding="utf-8") as f:
        f.write(meeting_transcript)

    print("회의 텍스트 추출 완료")


# # # [Step4] 회의 txt 파일을 blob storage에 업로드
def upload_txt_to_blob(output_dir, info, file_name):
    
    # BlobServiceClient 생성
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    local_file_path = f"{output_dir}/meeting_transcript.txt"   # 업로드할 파일 경로
    blob_name = f"{file_name}.txt"           # Blob에 저장될 파일 이름

    # 컨테이너의 BlobClient 생성
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # txt 파일 업로드
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)  # overwrite=True로 덮어쓰기 허용
    print(f"{local_file_path} 파일이 {container_name} 컨테이너에 {blob_name} 이름으로 업로드되었습니다.")

    # info.json 업로드
    info_json = json.dumps(info, ensure_ascii=False)
    blob_client_json = blob_service_client.get_blob_client(container=container_name, blob=f"{file_name}.json")
    blob_client_json.upload_blob(info_json, overwrite=True)
    print(f"info 파일이 {container_name} 컨테이너에 {file_name}.json 이름으로 업로드되었습니다.")

    # blob storage 조회
    # blobs = blob_service_client.get_container_client(container_name).list_blobs()
    # for blob in blobs:
    #     print(blob.name)