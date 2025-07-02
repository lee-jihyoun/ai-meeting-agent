let timerInterval; //타이머 인터벌 변수 
let startTime; //회의시작 시간
let startTimeFormatted; //회의시작 시간(yyyymmdd)
let audioCtx, micStream, processor, pcmData = []; // 오디오 처리 관련 변수 
const attendees = []; //참석자 목록 배열
let filename; //파일 이름 변수
let info; //회의 정보 변수

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

// 파일 이름에 Base62로 랜덤 문자 6자리를 추가하기 위한 함수
function makeBase62(length=6){
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length)); //랜덤 문자열 생성
    }
    return result;
}

async function uploadWavToAzureBlob(file, sasUrl, timeoutMs = 600000*180) { //3시간
    console.log("wav 파일 사이즈:", file.size);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(sasUrl, {
        method: "PUT",
        headers: {
            "x-ms-blob-type": "BlockBlob",
            "Content-Type": "audio/wav"
        },
        body: file,
        signal: controller.signal
    });
    if (!response.ok) {
      throw new Error("업로드 실패: " + response.statusText);
    }
    } catch (error) {
      if(error.name === 'AbortError') {
        throw new Error("업로드 시간 초과");
      }
      throw error;
    } finally {
      clearTimeout(timeoutId); //타임아웃 타이머 해제(메모리 누수 방지)
    }
    
    // alert("업로드 완료");
}

async function uploadWithRetry(file, sasUrl, maxAttempts = 3) {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        await uploadWavToAzureBlob(file, sasUrl);
        return; // 성공하면 함수 종료
      } catch (e) {
        if (attempt === maxAttempts) throw e;
        // 잠깐 대기 후 재시도(첫번째 실패 후 1초 뒤에 재시도. 2번째 실패 후 2초 뒤에 재시도)
        await new Promise(res => setTimeout(res, 1000 * attempt));
      }
    }
  }
  
function startMeeting() {
  const title = document.getElementById('meeting-title').value;
  const content = document.getElementById('meeting-content').value;
  const writerName = document.getElementById('writer-name').value;
  const writerPosition = document.getElementById('writer-position').value;
  const writerEmail = document.getElementById('writer-email').value;

  info =  {
      title: title,
      content : content,
      writer: [writerName, writerPosition, writerEmail],
      attendees: attendees,
      startTime: startTimeFormatted,
  };
  // 회의 시작
  const attendeeInputs = document.querySelectorAll('.input-row'); //참석자 입력 필드 선택
  attendees.length = 0; // 배열 초기화

  attendeeInputs.forEach(row => {
      const name = row.querySelector('.name-input').value; // 이름 가져오기
      const position = row.querySelector('.position-input').value; // 직급 가져오기
      const authorRole = row.querySelector('.role-input').value; // 역할 가져오기

      if(name && position !== '직급 선택' && authorRole) { // 유효성 검사
          attendees.push({ name, position, authorRole }); //유효한 참석자를 배열에 추가
          console.log("attendees:", attendees)
      }
  });

  // 비어 있는 참석자 배열 체크
  if (attendees.length === 0) {
      console.warn('No valid attendees provided');
      document.getElementById("response").innerText = 'Error: No valid attendees provided';
      return;
  }
  console.log("info:", info);
  return info;
}

function endMeeting(sas_url, filename, info) {
  //회의 종료
  fetch(`/transcribe?sas_url=${sas_url}&file_name=${encodeURIComponent(filename)}`, { //서버 요청
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

// // 파일 첨부 기능
// const docInput     = document.getElementById('docFile');
// const docSelectBtn = document.getElementById('docSelectBtn');
// const docListSpan  = document.getElementById('docList');

// docSelectBtn.addEventListener('click', () => docInput.click());

// docInput.addEventListener('change', () => {
//   const names = [...docInput.files].map(f => f.name).join(', ');
//   docListSpan.textContent = names || '선택된 파일 없음';
// });

// /* ========================================================
//    Blob 업로드 공통 함수 (타임아웃·MIME 자동 지정)
//    ======================================================== */
// async function uploadFileToAzureBlob(file, sasUrl, timeoutMs = 600_000) {
//   console.log('[UPLOAD] 시작:', file.name, 'size:', file.size);

//   const controller = new AbortController();
//   const timeoutId  = setTimeout(() => controller.abort(), timeoutMs);

//   try {
//     const res = await fetch(sasUrl, {
//       method : 'PUT',
//       headers: {
//         'x-ms-blob-type': 'BlockBlob',
//         'Content-Type'  : file.type || 'application/octet-stream'
//       },
//       body   : file,
//       signal : controller.signal
//     });
//     if (!res.ok) throw new Error('업로드 실패: ' + res.statusText);
//     console.log('[UPLOAD] 성공:', file.name);
//   } catch (err) {
//     if (err.name === 'AbortError') throw new Error('업로드 시간 초과');
//     throw err;
//   } finally {
//     clearTimeout(timeoutId);         // 메모리 누수 방지
//   }
// }

// async function uploadDocs(files) {
//   for (const file of files) {
//     /* ➊ 문서용 blob 이름과 함께 SAS URL 발급 */
//     const blobName = `plamingo_meeting_${startTimeFormatted}_${makeBase62(6)}_${file.name}`;
//     let sasUrl;
//     try {
//       const res        = await fetch(`/generate_sas_url?filename=${encodeURIComponent(blobName)}`);
//       ({ sas_url: sasUrl } = await res.json());          // ← 문서 전용 SAS URL
//       if (!sasUrl) throw new Error('SAS URL 생성 실패');
//     } catch (err) {
//       console.error('[DOC] SAS URL 오류:', err);
//       alert(`"${file.name}" 업로드 URL 생성에 실패했습니다.`);
//       continue;                                          // 다음 문서로
//     }

//     /* ➋ 발급받은 SAS URL로 업로드 (재시도 포함) */
//     try {
//       await uploadWithRetry(file, sasUrl);               // MIME 자동 지정
//       console.log('[DOC] 업로드 완료:', file.name);
//     } catch (err) {
//       console.error('[DOC] 업로드 실패:', err);
//       alert(`"${file.name}" 업로드 중 오류가 발생했습니다.`);
//     }
//   }
// }


// 유효성 검증 기능
const startBtn = document.getElementById('startBtn');
startBtn.addEventListener('click', async (e) => {
  e.preventDefault();

  const { emptyInvalid, emailInvalid, allValid } = validateAllInputs();

  if (!allValid) {
    // 1) 필수값이 비어 있으면 그 메시지 우선
    if (emptyInvalid) {
      alert('모든 필드를 입력한 후에 회의를 시작할 수 있습니다.');
    }
    // 2) 공란은 없는데 이메일 형식이 틀렸을 때
    else if (emailInvalid) {
      alert('올바른 형식의 이메일을 입력해 주세요.');
    }
    return;            // 검증 실패 → 회의 시작 중단
  }

  /* 모든 검증 통과 → 회의 시작 */
  try {
    const stream = await getMicStream();
    connectProcessor();
    startTimer();
    alert('회의가 시작되었습니다.');
    info = await startMeeting(); //전역변수에 저장
  } catch (err) {
    console.error('회의 시작 중 오류:', err);
    alert('마이크 권한 거부 또는 네트워크 오류가 발생했습니다.');
  }
});


document.getElementById("stopBtn").addEventListener("click", async () => {
    // 1. 버튼 숨기고 로딩 표시
    stopBtn.style.display = "none";
    loadingIndicator.style.display = "block";

    // 2. 비동기 작업(예: 업로드, 서버 요청 등)
    try {
        stopTimer(); // 타이머 종료
        processor.disconnect(); // 프로세서 연결 해제
        micStream.disconnect(); // 마이크 스트림 해제

        const merged = mergeBuffers(pcmData); // PCM 데이터 병합
        const wavBlob = encodeWAV(merged, audioCtx.sampleRate); // WAV 파일 생성

        pcmData = []; // PCM 데이터 초기화

        // 서버에서 SAS URL을 받아옴
        let sasUrl;
        try {
          filename = `plamingo_meeting_${startTimeFormatted}_${makeBase62(6)}`;
          // azure portal에서 CORS 허용을 해줘야 함.
          //generate_sas_url API 호출
          wavfile = filename + '.wav';
          // console.log("WAV 파일 이름: ", wavfile);
          const sasResponse = await fetch(`/generate_sas_url?filename=${encodeURIComponent(wavfile)}`);
          const data = await sasResponse.json();
          sasUrl = data.sas_url; // 서버에서 SAS URL을 받아옴
          console.log("SAS URL: ", sasUrl);
          if (!sasUrl) {
            console.error("SAS URL이 비어 있습니다:", sasUrl);
            alert("업로드 URL 생성에 실패했습니다. 다시 시도해 주세요.");
            return;
          }
        } catch (error) {
          console.error("SAS URL 생성 중 오류 발생:", error);
          alert("SAS URL 생성 중 오류가 발생했습니다. 다시 시도해 주세요.");
          return; // 오류 발생 시 함수 종료
        }

        // WAV Blob을 Azure Blob Storage에 업로드
        try{
          await uploadWavToAzureBlob(wavBlob, sasUrl);
          // uploadWithRetry(wavBlob, sasUrl);
          console.log("WAV 파일 업로드 완료");
        } catch (error) {
          console.error("WAV 파일 업로드 중 오류 발생:", error);
          alert("WAV 파일 업로드 중 오류가 발생했습니다. 다시 시도해 주세요.");
          return; // 오류 발생 시 함수 종료
        }

        // // 파일이 선택된 경우만 문서 업로드
        // if (docInput.files.length) {               // 파일이 선택된 경우만
        //   try {
        //     await uploadDocs(docInput.files);
        //     console.log('[DOCS] 업로드 완료');
        //   } catch (err) {
        //     console.error('[DOCS] 업로드 오류:', err);
        //     alert('문서 업로드 중 오류가 발생했습니다. WAV 업로드는 완료되었으니 이후 단계는 계속 진행합니다.');
        //   }
        // }


        // 회의 종료 요청
        endMeeting(sasUrl, filename, info); //transcribe API 호출
    } catch (error) {
        console.error("회의 종료 중 오류 발생:", error);
        alert("회의 종료 중 오류가 발생했습니다. 다시 시도해 주세요.");
        return; // 오류 발생 시 함수 종료
    } 
    finally {
        // 3. 작업 완료 후 로딩 숨기고 회의 시작 버튼 표시
        loadingIndicator.style.display = "none";
        startBtn.style.display = "block";
    }
});

// 참석자 입력행 추가 함수
function addAttendeeRow(button) {
    const row = button.parentElement; // 현재 버튼이 속한 부모 요소 선택
    if (button.textContent === '+') {
        const newRow = document.createElement('div'); // 새로운 행 생성
        newRow.className = "input-row row"; // 클래스 이름 설정
        newRow.innerHTML = `
            <input type="text" class="name-input" placeholder="이름 입력" required>
            <select class="position-input" required>
                <option value="" selected disabled>직급 선택</option>
                <option>전임</option>
                <option>선임</option>
                <option>책임</option>
            </select>
            <input type="text" class="role-input" placeholder="역할 입력" required>
            <button class="fab remove-btn" onclick="removeAttendeeRow(this)">-</button>
        `;
        document.getElementById("attendees").appendChild(newRow);
        // 새로 추가된 입력란에 이벤트 리스너 추가
        const newInputs = newRow.querySelectorAll('input, select');
        addEventListenersToInputs(newInputs);

    } else {
        removeAttendeeRow(button);
    }
}

//참석자 입력 행 제거 함수
function removeAttendeeRow(button) {
    const row = button.parentElement; //현재 버튼이 속한 부모 요소 선택
    document.getElementById("attendees").removeChild(row); //부모 요소에서 행 제거
}

/* =========================================================
   모든 입력 유효성 검사
   └ return: { emptyInvalid: bool, emailInvalid: bool, allValid: bool }
   ========================================================= */
function validateAllInputs() {
  let emptyInvalid = false;   // 필수값 누락
  let emailInvalid = false;   // 이메일 형식·도메인 오류

  /* 1) 페이지의 모든 input / select / textarea 순회 */
  document.querySelectorAll('input, select, textarea').forEach(el => {

    /* 1-A) 공란(또는 SELECT 미선택) 여부 우선 확인 */
    const isBlank = !el.value.trim() ||
                    (el.tagName === 'SELECT' && el.selectedIndex === 0);

    if (isBlank) {
      el.classList.add('invalid');
      emptyInvalid = true;
      return;                       // 공란이면 형식검사는 볼 필요 X
    }

    /* 1-B) 형식 검증 (= HTML5 checkValidity) */
    if (!el.checkValidity()) {      // 여기서 이메일·숫자범위·pattern 검사 (html에 있는 type=email을 브라우저에서 검사)
      el.classList.add('invalid');
      if (el.id === 'writer-email') emailInvalid = true;
      else                          emptyInvalid = true;   // 드물지만 pattern 있는 다른 필드
    } else {
      el.classList.remove('invalid');
    }
  });

  return {
    emptyInvalid,
    emailInvalid,
    allValid: !(emptyInvalid || emailInvalid)
  };
}


function addEventListenersToInputs(nodeList) {
  const inputs = nodeList ?? document.querySelectorAll('input, select, textarea');

  inputs.forEach(el => {
    // 값이 바뀌면 빨간 표시만 없애 주고, 전체 검증은 하지 않음
    const clearOnly = () => el.classList.remove('invalid');

    el.addEventListener('input',  clearOnly);  // text·textarea
    el.addEventListener('change', clearOnly);  // select
  });
}



// DOM 로드 후에 함수 호출
document.addEventListener('DOMContentLoaded', () => {
addEventListenersToInputs();  // 함수 정의 후 호출하므로 오류 없음
});

// 페이지 로드 시 모든 입력란에 이벤트 리스너 추가
window.onload = () => {
    const allInputs = document.querySelectorAll('input[required], textarea[required], select[required]');
    addEventListenersToInputs(allInputs);
    document.getElementById('meeting-title').focus();
};


// 서버 상태 체크 및 다운 시 배너 표시
async function checkServerStatus() {
  try {
    const res = await fetch('/healthcheck', { cache: 'no-store' }); // 캐시 무시
    if (!res.ok) throw new Error('서버 응답 오류');
    hideServerDownBanner(); // 정상일 때 배너 숨김
  } catch (e) {
    showServerDownBanner(); // 서버 다운 시 배너 표시
    stopTimer();
  }
}

setInterval(checkServerStatus, 5000); // 5초마다 체크

function showServerDownBanner() {
  // 화면 상단이나 중앙에 서버 장애 안내 배너 표시
  document.getElementById('serverStatus').style.display = 'block';
}
function hideServerDownBanner() {
  document.getElementById('serverStatus').style.display = 'none';
}