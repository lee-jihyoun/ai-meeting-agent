from flask import Flask, request
import azure.cognitiveservices.speech as speechsdk
import threading
import wave
import os

# [서버] 오디오 수신 + Azure Speech 연동 (Flask + Azure Speech SDK)

# Flask 앱 생성 (Flask 서버 설정)
app = Flask(__name__)
AUDIO_BUFFER_FILE = "temp_audio.wav"

# Azure 설정
speech_key = "YOUR_SPEECH_KEY"
region = "YOUR_REGION"

# 오디오 수신 endpoint
# client_audio_stream.py 로부터 /stream_audio POST 요청 수신
@app.route('/stream_audio', methods=['POST'])
def receive_audio():
    audio_data = request.data

    with open(AUDIO_BUFFER_FILE, "wb") as f:
        # wav_header() 호출
        f.write(wav_header(len(audio_data)))
        f.write(audio_data)

    # 별도 쓰레드에서 인식 시작
    # run_speech_recognition() 호출
    threading.Thread(target=run_speech_recognition, args=(AUDIO_BUFFER_FILE,)).start()
    return '', 200

# WAV 헤더 생성 함수
def wav_header(data_length):
    """16bit PCM WAV 헤더 생성"""
    import struct
    num_channels = 1
    sample_rate = 16000
    bits_per_sample = 16
    byte_rate = sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = data_length
    file_size = 36 + data_size
    return struct.pack('<4sI4s4sIHHIIHH4sI',
                       b'RIFF', file_size, b'WAVE', b'fmt ', 16, 1, num_channels,
                       sample_rate, byte_rate, block_align, bits_per_sample,
                       b'data', data_size)

# STT 처리 및 Blob 업로드 함수
def run_speech_recognition(filename):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=region)
    audio_config = speechsdk.audio.AudioConfig(filename=filename)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"📝 인식 결과: {result.text}")
    else:
        print(f"❗ 인식 실패 또는 오류: {result.reason}")

    # 업로드
    try:
        blob_name = f"audio/meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        upload_to_blob(filename, blob_container, blob_name)
    except Exception as e:
        print(f"🚫 업로드 실패: {e}")

    os.remove(filename)

# Blob 업로드 함수
def upload_to_blob(file_path, container_name, blob_name):
    blob_conn_str = os.environ["AZURE_BLOB_CONN_STR"]
    blob_service_client = BlobServiceClient.from_connection_string(blob_conn_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    with open(file_path, "rb") as audio_file:
        blob_client.upload_blob(audio_file, overwrite=True)

    print(f"✅ Blob 업로드 완료: {blob_name}")

# 서버 실행
if __name__ == '__main__':
    app.run(debug=True)
