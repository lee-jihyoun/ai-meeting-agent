import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import MeetingForm from './components/MeetingForm';
import Timer from './components/Timer';
import AudioRecorder from './hooks/useAudioRecorder';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  const [serverOnline, setServerOnline] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [meetingInfo, setMeetingInfo] = useState(null);

  const audioRecorderRef = useRef(new AudioRecorder());

  // 서버 상태 체크
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/healthcheck`, { cache: 'no-store' });
        if (!res.ok) throw new Error('서버 응답 오류');
        setServerOnline(true);
      } catch (e) {
        setServerOnline(false);
        if (isRecording) {
          handleStopMeeting();
        }
      }
    };

    const interval = setInterval(checkServerStatus, 5000);
    return () => clearInterval(interval);
  }, [isRecording]);

  const handleStartMeeting = async (info) => {
    try {
      await audioRecorderRef.current.startRecording();
      setIsRecording(true);
      setStartTime(Date.now());
      setMeetingInfo(info);
      alert('회의가 시작되었습니다.');
    } catch (err) {
      console.error('회의 시작 중 오류:', err);
      alert('마이크 권한 거부 또는 네트워크 오류가 발생했습니다.');
    }
  };

  const handleStopMeeting = async () => {
    setIsLoading(true);

    try {
      const wavBlob = await audioRecorderRef.current.stopRecording();

      // 파일 이름 생성
      const startTimeFormatted = formatDateLocal(startTime);
      const randomStr = makeBase62(6);
      const filename = `plamingo_meeting_${startTimeFormatted}_${randomStr}`;
      const wavfile = filename + '.wav';

      // SAS URL 생성
      const sasResponse = await fetch(
        `${API_BASE_URL}/generate_sas_url?filename=${encodeURIComponent(wavfile)}`
      );
      const data = await sasResponse.json();
      const sasUrl = data.sas_url;

      if (!sasUrl) {
        alert("업로드 URL 생성에 실패했습니다. 다시 시도해 주세요.");
        return;
      }

      // WAV 파일 업로드
      await uploadWavToAzureBlob(wavBlob, sasUrl);
      console.log("WAV 파일 업로드 완료");

      // 회의 종료 요청
      await fetch(
        `${API_BASE_URL}/transcribe?sas_url=${encodeURIComponent(sasUrl)}&file_name=${encodeURIComponent(filename)}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(meetingInfo)
        }
      );

      alert('회의가 종료되었습니다. 회의록이 생성 중입니다.');
    } catch (error) {
      console.error("회의 종료 중 오류 발생:", error);
      alert("회의 종료 중 오류가 발생했습니다. 다시 시도해 주세요.");
    } finally {
      setIsLoading(false);
      setIsRecording(false);
      setStartTime(null);
      setMeetingInfo(null);
    }
  };

  return (
    <div className="App">
      {!serverOnline && (
        <div className="server-status-banner show">
          서버와 연결이 끊겼습니다. 잠시 후 다시 시도해 주세요.
        </div>
      )}

      <h1>Plamingo</h1>

      <MeetingForm
        onStart={handleStartMeeting}
        isRecording={isRecording}
        isLoading={isLoading}
      />

      <Timer startTime={startTime} isRunning={isRecording} />

      <div className="container buttons">
        {!isRecording && !isLoading && (
          <button
            className="start-btn"
            onClick={() => {
              const formData = document.getElementById('meeting-form-data');
              if (formData) formData.dispatchEvent(new Event('submit'));
            }}
          >
            회의 시작
          </button>
        )}

        {isRecording && (
          <button className="stop-btn" onClick={handleStopMeeting}>
            회의 종료
          </button>
        )}

        {isLoading && (
          <div>
            <span>진행 중입니다...</span>
            <span className="spinner"></span>
          </div>
        )}
      </div>
    </div>
  );
}

// Utility functions
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

function makeBase62(length = 6) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

async function uploadWavToAzureBlob(file, sasUrl, timeoutMs = 600000 * 180) {
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
    if (error.name === 'AbortError') {
      throw new Error("업로드 시간 초과");
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

export default App;
