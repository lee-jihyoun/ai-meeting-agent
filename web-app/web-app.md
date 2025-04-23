# 전체 아키텍처 플로우

[1] 음성 수집

[2] Azure Blob Storage 저장

[3] Azure Speech -> 텍스트 변환 (STT)

[4] OpenAI -> 요약

[5] Azure Cognitive Search -> 검색 가능하게

[6] 이메일 발송 (Logic Apps or SMTP)


# 전체 흐름

[웹 브라우저] index.html "회의시작" 버튼

[Flask 서버] web-app.py (/start_meeting)

[클라이언트 실행] client-audio-stream.py

[오디오 전송] -> [Flask STT 서버(오디오 수신 + Azure Speech 연동)] server-stt.py

[Azure Speech SDK STT 결과 출력]


## (Teams Meeting Bot 으로 오디오 스트림 수신이 아니라) 사용자의 마이크에서 실시간 캡처

Teams 회의중 사용자의 마이크에서 직접 오디오를 캡처해서

실시간으로 azure Service로 전송

자막처럼 실시간으로 텍스트 출력


### [구성]

사용자 PC/웹페이지

(마이크 입력) -> python 앱 ->

(실시간 STT) -> Azure Speech Service ->

콘솔 또는 웹에 텍스트 출력


### [목표 흐름]

[웹페이지 : 회의 시작 버튼] : web-app/templates/idex.html

[Flask 웹서버 : /start_meeing 엔드포인트] : web-app/webapp.py

[로컬 STT 클라이언트 subprocess 실행 (마이크 or 시스템 오디오)] : speech-service/client-audio-stream.py

[Azure Speech 인식]

