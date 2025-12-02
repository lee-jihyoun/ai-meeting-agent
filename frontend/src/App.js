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
        const res = await fetch(`${API_BASE_URL}/healthcheck`, {
          cache: 'no-store',
        });
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
        `${API_BASE_URL}/generate_sas_url?filename=${encodeURIComponent(
          wavfile
        )}`
      );
      const data = await sasResponse.json();
      const sasUrl = data.sas_url;

      if (!sasUrl) {
        alert('업로드 URL 생성에 실패했습니다. 다시 시도해 주세요.');
        return;
      }

      // WAV 파일 업로드
      await uploadWavToAzureBlob(wavBlob, sasUrl);
      console.log('WAV 파일 업로드 완료');

      // 회의 종료 요청
      await fetch(
        `${API_BASE_URL}/transcribe?sas_url=${encodeURIComponent(
          sasUrl
        )}&file_name=${encodeURIComponent(filename)}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(meetingInfo),
        }
      );

      alert('회의가 종료되었습니다. 회의록이 생성 중입니다.');
    } catch (error) {
      console.error('회의 종료 중 오류 발생:', error);
      alert('회의 종료 중 오류가 발생했습니다. 다시 시도해 주세요.');
    } finally {
      setIsLoading(false);
      setIsRecording(false);
      setStartTime(null);
      setMeetingInfo(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {!serverOnline && (
        <div className="fixed top-0 left-0 w-full bg-red-500 text-white text-center py-3 px-4 z-50 shadow-lg">
          <span className="font-semibold">
            ⚠️ 서버와 연결이 끊겼습니다. 잠시 후 다시 시도해 주세요.
          </span>
        </div>
      )}

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-2 pb-2">
            Plamingo
          </h1>
          <p className="text-gray-600 text-sm">AI Meeting Assistant</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <MeetingForm
            onStart={handleStartMeeting}
            isRecording={isRecording}
            isLoading={isLoading}
          />
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8 mb-6">
          <Timer startTime={startTime} isRunning={isRecording} />
        </div>

        <div className="flex justify-center items-center gap-4">
          {!isRecording && !isLoading && (
            <button
              type="button"
              className="bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-4 px-8 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
              onClick={() => {
                console.log('회의 시작 버튼 클릭됨');
                const formData = document.getElementById('meeting-form-data');
                console.log('폼 찾음:', formData);
                if (formData) {
                  const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
                  formData.dispatchEvent(submitEvent);
                } else {
                  console.error('폼을 찾을 수 없습니다');
                }
              }}
            >
              <span className="flex items-center gap-2">
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                    clipRule="evenodd"
                  />
                </svg>
                회의 시작
              </span>
            </button>
          )}

          {isRecording && (
            <button
              className="bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white font-bold py-4 px-8 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200"
              onClick={handleStopMeeting}
            >
              <span className="flex items-center gap-2">
                <svg
                  className="w-5 h-5"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z"
                    clipRule="evenodd"
                  />
                </svg>
                회의 종료
              </span>
            </button>
          )}

          {isLoading && (
            <div className="flex items-center gap-2 text-blue-600 font-semibold">
              <span>진행 중입니다...</span>
              <span className="spinner"></span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Utility functions
function formatDateLocal(timestamp) {
  const date = new Date(timestamp);
  const z = (n) => n.toString().padStart(2, '0');
  return (
    date.getFullYear().toString() +
    z(date.getMonth() + 1) +
    z(date.getDate()) +
    '_' +
    z(date.getHours()) +
    z(date.getMinutes()) +
    z(date.getSeconds())
  );
}

function makeBase62(length = 6) {
  const chars =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
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
      method: 'PUT',
      headers: {
        'x-ms-blob-type': 'BlockBlob',
        'Content-Type': 'audio/wav',
      },
      body: file,
      signal: controller.signal,
    });
    if (!response.ok) {
      throw new Error('업로드 실패: ' + response.statusText);
    }
  } catch (error) {
    if (error.name === 'AbortError') {
      throw new Error('업로드 시간 초과');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

export default App;
