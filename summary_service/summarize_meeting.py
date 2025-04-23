# Blob에 저장된 WAV 파일 -> 텍스트 요약 생성
# 1. Blob stroage 에서 WAV 파일 다운로드
# 2. Azure Speech SDK로 텍스트 전사
# 3. 전사된 텍스트를 OpenAI GPT에 요약 요청
import os
from azure.storage.blob import BlobServiceClient
import azure.cognitiveservices.speech as speechsdk
import openai

# TODO .env 에서 받아오도록 처리 필요
AZURE_BLOB_CONN_STR = os.getenv("AZURE_BLOB_CONN_STR")
AZURE_CONTAINER_NAME = "audio"
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION")
OPENAI_KEY = os.getenv("OPENAI_KEY")
openai.api_key = OPENAI_KEY

# 1. Blob stroage 에서 WAV 파일 다운로드
def download_blob(filename, local_path):
    blob_service = BlobServiceClient.from_connection_string(AZURE_BLOB_CONN_STR)
    blob_client = blob_service.get_container_client(AZURE_CONTAINER_NAME).get_blob_client(filename)
    with open(local_path, "wb") as f:
        f.write(blob_client.download_blob().readall())
    return local_path

# 2. Azure Speech SDK로 텍스트 전사
def transcribe_audio(file_path):
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    else:
        return "[오류] 음성 인식 실패"

# 3. 전사된 텍스트를 OpenAI GPT에 요약 요청
def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "다음 회의 내용을 요약해줘."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

# 요약된 결과 summary 리턴
def summarize_meeting(blob_filename):
    local_file = f"./temp/{blob_filename}"
    download_blob(blob_filename, local_file)
    transcript = transcribe_audio(local_file)
    summary = summarize_text(transcript)
    return summary
