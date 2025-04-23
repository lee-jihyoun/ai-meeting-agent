import sounddevice as sd
import requests
import numpy as np
import time
import threading

# [클라이언트] 마이크/시스템 사운드 수집
SERVER_URL = "http://localhost:5000/stream_audio"
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION = 1  # 초 단위로 전송 (1초마다)

def stream_audio():
    def callback(indata, frames, time_info, status):
        audio_bytes = indata.astype(np.int16).tobytes()
        try:
            # /stream_audio 로 POST 요청
            requests.post(SERVER_URL, data=audio_bytes, headers={"Content-Type": "application/octet-stream"})
        except Exception as e:
            print("전송 실패:", e)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', callback=callback):
        print("🎙 시스템 오디오 캡처 중... 중지하려면 Ctrl+C")
        while True:
            time.sleep(1)


if __name__ == "__main__":
    stream_audio()
