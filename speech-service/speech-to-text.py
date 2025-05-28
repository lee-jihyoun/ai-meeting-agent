import azure.cognitiveservices.speech as speechsdk
import time
import os
from dotenv import load_dotenv



def start_speech_recognition(): 

    load_dotenv()
    speech_key = os.getenv('AI_SERVICE_KEY')
    service_region = os.getenv('AI_SERVICE_REGION')
    endpoint = os.getenv('AI_SERVICE_ENDPOINT')  # 필요 시 사용

    print(speech_key, service_region, endpoint)

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    # endpoint가 별도로 필요 없는 경우도 있지만, 특정 Custom Speech 등의 시나리오에서는 endpoint 지정 가능
    speech_config.speech_recognition_language = "ko-KR"


    # 오디오 소스 설정 (마이크 사용)
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

# Speech Recognizer 객체 생성
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
##

    # 결과 수신 핸들러
    def recognized_handler(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print(f"인식됨 : {evt.result.text}")
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print("인식되지 않음")

    def canceled_handler(evt):
        print(f"오류 : {evt.reason}")
        if evt.reason == speechsdk.CancellationReason.Error: 
            print(f"오류 코드 : {evt.error_code}")
            print(f"세부 정보 : {evt.error_details}")

    # 핸들러 연결
    speech_recognizer.recognized.connect(recognized_handler)
    speech_recognizer.canceled.connect(canceled_handler)

    # 인식 시작
    print("🎙️ 한국어 음성 인식 시작 (10분 동안)... 말을 해보세요.")
    speech_recognizer.start_continuous_recognition()

    # 10분 동안 대기
    time.sleep(600)  # 600초 = 10분

    # 인식 종료
    speech_recognizer.stop_continuous_recognition()
    print("✅ 인식 종료")

    # print("Say something...")

    # # 음성을 텍스트로 변환하고 출력
    # result = speech_recognizer.recognize_once()
    # print("Recognized: {}".format(result.text))

if __name__ == "__main__":
    start_speech_recognition()