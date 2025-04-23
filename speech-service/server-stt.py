from flask import Flask, request
import azure.cognitiveservices.speech as speechsdk
import threading
import os
import struct
import datetime
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
from azure.storage.blob import BlobServiceClient

# Flask 앱 생성 (Flask 서버 설정)
app = Flask(__name__)

AUDIO_BUFFER_FILE = "temp_audio.wav"

# Azure 설정 (환경변수 또는 직접 입력)
speech_key = "YOUR_SPEECH_KEY"
region = "YOUR_REGION"

# TODO .env 에서 불러오는 형태로 수정할것
blob_conn_str = os.getenv("AZURE_BLOB_CONN_STR")  # .env 또는 시스템 환경변수에서 불러오기
blob_container = "meeting-audio"

# 오디오 수신 endpoint
# client_audio_stream.py 로부터 /stream_audio POST 요청 수신
@app.route('/stream_audio', methods=['POST'])
def receive_audio():
    threading.Thread(target=record_process_upload).start()
    return '', 200

# 오디오 녹음
def record_audio(filename, duration=10, fs=16000):
    print("🎙️ 녹음 시작...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, fs, audio)
    print(f"🎧 녹음 완료: {filename}")

# STT 처리 및 Blob 업로드 함수 (Azure Speech to Text)
def run_speech_recognition(filename):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
    audio_config = speechsdk.audio.AudioConfig(filename=filename)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"📝 인식 결과: {result.text}")
    else:
        print(f"❗ 인식 실패 또는 오류: {result.reason}")

# Blob 업로드 함수 (Azure Blob Storage 업로드)
def upload_to_blob(file_path, container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(blob_conn_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    with open(file_path, "rb") as audio_file:
        blob_client.upload_blob(audio_file, overwrite=True)

    print(f"✅ Blob 업로드 완료: {blob_name}")

# 전체 흐름 통합: 녹음 → STT → 업로드
def record_process_upload():
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"meeting_{now}.wav"

    try:
        record_audio(filename, duration=10)
        run_speech_recognition(filename)
        upload_to_blob(filename, blob_container, f"audio/{filename}")
    except Exception as e:
        print(f"🚫 오류 발생: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)


# 서버 실행(서버 시작)
if __name__ == '__main__':
    app.run(debug=True)
