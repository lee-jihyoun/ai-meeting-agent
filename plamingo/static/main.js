
let timerInterval; //타이머 인터벌 변수 
let startTime; //회의시작 시간
let startTimeFormatted; //회의시작 시간(yyyymmdd)
let audioCtx, micStream, processor, pcmData = []; // 오디오 처리 관련 변수 
const attendees = []; //참석자 목록 배열

// 타이머 시작 함수 
function startTimer() {
    startTime = Date.now(); // 현재 시간을 시작 시간으로 설정
    startTimeFormatted = formatDateLocal(startTime)
    timerInterval = setInterval(updateTimer, 1000); //1초마다 타이머 업데이트 
    document.getElementById("startBtn").style.display = "none"; //시작 버튼 숨기기 
    document.getElementById("stopBtn").style.display = "inline-block"; //종료 버튼 보이기
}

//타이머 업데이트 함수
function updateTimer() {
    let elapsed = Math.floor((Date.now() - startTime) / 1000); //경과 시간 계산
    let hours = String(Math.floor(elapsed / 3600)).padStart(2, '0'); //시간 계산
    let minutes = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0'); //분 계산
    let seconds = String(elapsed % 60).padStart(2, '0'); //초 계산
    document.getElementById("timerDisplay").innerText = `${hours}:${minutes}:${seconds}`; //경과시간 표시
}

//타이머 종료 함수
function stopTimer() {
    clearInterval(timerInterval); //타이머 인터벌 종료
    endTime = Date.now()
    document.getElementById("stopBtn").style.display = "none"; //종료 버튼 숨기기
}

// 시간 변환 함수 (YYYYMMDD_HHMMSS)
function formatDateLocal(timestamp) {
    const date = new Date(timestamp);
    const z = n => n.toString().padStart(2, '0');
    return (
    date.getFullYear().toString() +
    z(date.getMonth() + 1) +
    z(date.getDate()) + '_' +
    z(date.getHours()) +
    z(date.getMinutes()) +
    z(date.getSeconds())
    );
}

// 마이크 스트림을 가져오는 비동기 함수
async function getMicStream() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); //오디오 입력 스트림 요청
    audioCtx = new (window.AudioContext || window.webkitAudioContext)(); //오디오 컨텍스트 생성
    micStream = audioCtx.createMediaStreamSource(stream); //마이크 스트림은 소스에 연결
    return stream;
}

//오디오 프로세서 연결 함수 
function connectProcessor() {
    processor = audioCtx.createScriptProcessor(4096, 1, 1); //스크립트 프로세서 생성
    //오디오 입력 처리 메소드
    processor.onaudioprocess = e => {
    pcmData.push(new Float32Array(e.inputBuffer.getChannelData(0))); //PCM 데이터 저장 
    };
    micStream.connect(processor); //마이크 스트림을 프로세서에 연결
    processor.connect(audioCtx.destination); //프로세서를 오디오 출력에 연결
}

//PCM 버퍼 병합 함수
function mergeBuffers(chunks) {
    let length = chunks.reduce((sum, c) => sum + c.length, 0); //총 길이 계산 
    const result = new Float32Array(length); //새로운 Float32Array 생성
    let offset = 0;
    chunks.forEach(chunk => { //각 청크를 결과 배열에 복사 
    result.set(chunk, offset);
    offset += chunk.length;
    });
    return result; // 병합된 배열 반환
}

//WAV 인코딩 함수 
function encodeWAV(samples, sampleRate) {
    const buffer = new ArrayBuffer(44 + samples.length * 2); //WAV 포맷에 필요한 길이
    const view = new DataView(buffer); // 데이터뷰 생성
    writeString(view, 0, 'RIFF'); //WAV 헤더 생성
    view.setUint32(4, 36 + samples.length * 2, true); //파일 크기
    writeString(view, 8, 'WAVE'); //WAV 헤더
    writeString(view, 12, 'fmt '); //포맷 헤더
    view.setUint32(16, 16, true); //포맷 사이즈
    view.setUint16(20, 1, true); //오디오 포맷
    view.setUint16(22, 1, true); //채널 수
    view.setUint32(24, sampleRate, true); // 샘플링 레이트
    view.setUint32(28, sampleRate * 2, true); //바이트율
    view.setUint16(32, 2, true); //블록 정수
    view.setUint16(34, 16, true); //비트 수 
    writeString(view, 36, 'data'); //데이터 헤더
    view.setUint32(40, samples.length * 2, true); //데이터 크기
    let offset = 44; //데이터 시작 오프셋
    for (let i = 0; i < samples.length; i++, offset += 2) { //샘플 데이터를 작성
    let s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true); //샘플을 16비트 정수로 변환
    }
    return new Blob([view], { type: 'audio/wav' }); // Blob 반환
}

// 문자열을 데이터 뷰에 작성하는 함수 
function writeString(view, offset, str) {
    for (let i = 0; i < str.length; i++) {
    view.setUint8(offset + i, str.charCodeAt(i)); //문자열의 각 문자를 바이트로 변환
    }
}

async function uploadWavToAzureBlob(file, sasUrl) {
    const response = await fetch(sasUrl, {
        method: "PUT",
        headers: {
            "x-ms-blob-type": "BlockBlob",
            "Content-Type": "audio/wav"
        },
        body: file
    });

    if (!response.ok) {
        throw new Error("업로드 실패: " + response.statusText);
    }
    alert("업로드 완료");
}

// 요청을 보내는 함수
function sendRequest(meetingAction, sas_url) {
    const title = document.getElementById('meeting-title').value;
    const content = document.getElementById('meeting-content').value;
    const writerName = document.getElementById('writer-name').value;
    const writerPosition = document.getElementById('writer-position').value;
    const writerEmail = document.getElementById('writer-email').value;

    const info =  {
        meetingAction: meetingAction,
        title: title,
        content : content,
        writer: [writerName, writerPosition, writerEmail],
        attendees: attendees,
        startTime: startTimeFormatted,
    };
    // 회의 시작
    if (meetingAction == 'startMeeting') {
        const attendeeInputs = document.querySelectorAll('.input-row'); //참석자 입력 필드 선택
        attendees.length = 0; // 배열 초기화

        attendeeInputs.forEach(row => {
            const name = row.querySelector('.name-input').value; // 이름 가져오기
            const position = row.querySelector('.position-input').value; // 직급 가져오기
            const authorRole = row.querySelector('.role-input').value; // 역할 가져오기

            if(name && position !== '직급 선택' && authorRole) { // 유효성 검사
                attendees.push({ name, position, authorRole }); //유효한 참석자를 배열에 추가
                console.log("sendRequest attendees : ", attendees)
            }
    });

    // 비어 있는 참석자 배열 체크
    if (attendees.length === 0) {
        // TODO: 화면에 필수 값 경고 표시
        console.warn('No valid attendees provided');
        document.getElementById("response").innerText = 'Error: No valid attendees provided';
        return;
    }
    console.log("sendRequest info : ", info);
    }

    //회의 종료
    else if (meetingAction == 'endMeeting') {   
        fetch(`/transcribe?sas_url=${sas_url}`, { //서버 요청
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(info)
        })
        .then(res => {
            console.log('서버 응답:', res); // ① 서버 응답 확인
            if (!200) throw new Error('HTTP ' + res.status);
            return res.json();                // ① JSON 파싱
        })
        .catch(console.error);
    }
}

// 회의 시작 버튼 클릭 이벤트 리스너
document.getElementById("startBtn").addEventListener("click", async () => {
    const stream = await getMicStream(); //마이크 스트림 가져오기
    connectProcessor(); //오디오 프로세서 연결
    startTimer(); //타이머 시작
    sendRequest("startMeeting", null); //회의 시작 요청
});


document.getElementById("stopBtn").addEventListener("click", async () => {
    processor.disconnect(); // 프로세서 연결 해제
    micStream.disconnect(); // 마이크 스트림 해제
    const merged = mergeBuffers(pcmData); // PCM 데이터 병합
    const wavBlob = encodeWAV(merged, audioCtx.sampleRate); // WAV 파일 생성

    pcmData = []; // PCM 데이터 초기화

    // 1. 서버에서 SAS URL을 받아옵니다
    const filename = `plamingo_meeting_${startTimeFormatted}.wav`;
    // azure portal에서 CORS 허용을 해줘야 함.

    //generate_sas_url API 호출
    const sasResponse = await fetch(`/generate_sas_url?filename=${encodeURIComponent(filename)}`);
    const data = await sasResponse.json();
    const sasUrl = data.sas_url; // 서버에서 SAS URL을 받아옴
    console.log("SAS URL: ", sasUrl);

    // 2. WAV Blob을 Azure Blob Storage에 업로드
    await uploadWavToAzureBlob(wavBlob, sasUrl);
    console.log("WAV 파일 업로드 완료");

    // 3. 회의 종료 요청
    sendRequest("endMeeting", sasUrl); //transcribe API 호출
    stopTimer(); // 타이머 종료

    // TODO: 화면에 api 상태 표시??
    document.getElementById("startBtn").style.display = "inline-block"; // 시작 버튼 보이기
});

// 참석자 입력행 추가 함수
function addAttendeeRow(button) {
    const row = button.parentElement; //현재 버튼이 속한 부모 요소 선택
    if (button.textContent === '+') {
    const newRow = document.createElement('div'); //새로운 행 생성
    newRow.className = "input-row row"; //클래스 이름 설정
    newRow.innerHTML = `
        <input type="text" placeholder="이름">
        <select>
            <option>직급 선택</option>
            <option>전임</option>
            <option>선임</option>
            <option>책임</option>
        </select>
        <input type="text" placeholder="역할" required>
        <button class="fab remove-btn" onclick="removeAttendeeRow(this)">-</button>
    `;
    document.getElementById("attendees").appendChild(newRow); //새로운 행 추가
    } else {
    removeAttendeeRow(button); //참석자 제거
    }
}

//참석자 입력 행 제거 함수
function removeAttendeeRow(button) {
    const row = button.parentElement; //현재 버튼이 속한 부모 요소 선택
    document.getElementById("attendees").removeChild(row); //부모 요소에서 행 제거
}

// 필수 입력값 validation check
const inputs = document.querySelectorAll('input[required], textarea[required], select[required]');
const startBtn = document.getElementById('startBtn');
const meetingTitleInput = document.getElementById('meeting-title');

const validateInputs = () => {
    let allValid = true;
    inputs.forEach(input => {
        if(input.value.trim() === '' || (input.tagName === 'SELECT' && input.selectedIndex === 0)) {
            input.classList.add('invalid'); // invalid 클래스 추가 
            allValid = false;
        } else {
            input.classList.remove('invalid'); // invalid 클래스 제거
        }
    });
    startBtn.disabled = !allValid; // 모든 input이 유효할 때만 버튼 활성화

};



// 입력 필드 및 select에 이벤트 리스너 추가
inputs.forEach(input => {
    input.addEventListener('input', validateInputs);
    input.addEventListener('blur', validateInputs);
    input.addEventListener('change', validateInputs); // select의 변경 처리를 위한 이벤트
});



// 회의 시작 버튼 클릭 이벤트

startBtn.addEventListener('click', () => {
    if(validateInputs()) {
        alert('회의를 시작합니다.');
    }
});



// 초기 placeholder 색상으로 설정 (optional)
// validateInputs(); // 페이지 로드 시 유효성 검사 실행

// 페이지 로드 시 회의 제목 input에 포커스 주기
window.onload = () => {
    meetingTitleInput.focus(); //회의 제목 input 에 포커스 
}