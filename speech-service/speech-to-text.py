import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv

load_dotenv()

speech_key = os.getenv('SPEECH_KEY')
service_region = os.getenv('SPEECH_REGION')
endpoint = os.getenv('SPEECH_ENDPOINT')  # 필요 시 사용

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# endpoint가 별도로 필요 없는 경우도 있지만, 특정 Custom Speech 등의 시나리오에서는 endpoint 지정 가능
