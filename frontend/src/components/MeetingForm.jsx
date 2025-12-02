import React, { useState } from 'react';

function MeetingForm({ onStart, isRecording, isLoading }) {
  const [meetingTitle, setMeetingTitle] = useState('');
  const [meetingContent, setMeetingContent] = useState('');
  const [writerName, setWriterName] = useState('');
  const [writerPosition, setWriterPosition] = useState('');
  const [writerEmail, setWriterEmail] = useState('');
  const [attendees, setAttendees] = useState([
    { name: '', position: '', authorRole: '' }
  ]);

  const [errors, setErrors] = useState({});

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const validateForm = () => {
    const newErrors = {};

    if (!meetingTitle.trim()) newErrors.meetingTitle = true;
    if (!meetingContent.trim()) newErrors.meetingContent = true;
    if (!writerName.trim()) newErrors.writerName = true;
    if (!writerPosition) newErrors.writerPosition = true;
    if (!writerEmail.trim() || !validateEmail(writerEmail)) newErrors.writerEmail = true;

    attendees.forEach((attendee, index) => {
      if (!attendee.name.trim() || !attendee.position || !attendee.authorRole.trim()) {
        newErrors[`attendee_${index}`] = true;
      }
    });

    setErrors(newErrors);

    if (Object.keys(newErrors).length > 0) {
      if (newErrors.writerEmail && writerEmail.trim()) {
        alert('올바른 형식의 이메일을 입력해 주세요.');
      } else {
        alert('모든 필드를 입력한 후에 회의를 시작할 수 있습니다.');
      }
      return false;
    }

    return true;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateForm()) {
      const startTimeFormatted = formatDateLocal(Date.now());
      const info = {
        title: meetingTitle,
        content: meetingContent,
        writer: [writerName, writerPosition, writerEmail],
        attendees: attendees.filter(a => a.name && a.position && a.authorRole),
        startTime: startTimeFormatted,
      };
      onStart(info);
    }
  };

  const addAttendee = () => {
    setAttendees([...attendees, { name: '', position: '', authorRole: '' }]);
  };

  const removeAttendee = (index) => {
    setAttendees(attendees.filter((_, i) => i !== index));
  };

  const updateAttendee = (index, field, value) => {
    const newAttendees = [...attendees];
    newAttendees[index][field] = value;
    setAttendees(newAttendees);
  };

  const clearError = (field) => {
    const newErrors = { ...errors };
    delete newErrors[field];
    setErrors(newErrors);
  };

  return (
    <form id="meeting-form-data" onSubmit={handleSubmit} className="space-y-6">
      {/* 회의 제목 */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-gray-700">회의 제목</label>
        <input
          type="text"
          placeholder="회의 제목을 입력하세요."
          value={meetingTitle}
          onChange={(e) => {
            setMeetingTitle(e.target.value);
            clearError('meetingTitle');
          }}
          className={`w-full px-4 py-3 rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.meetingTitle
              ? 'border-red-300 bg-red-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
          disabled={isRecording || isLoading}
          required
        />
      </div>

      {/* 회의 내용 */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-gray-700">회의 내용</label>
        <textarea
          rows="4"
          placeholder="회의 내용을 입력하세요."
          value={meetingContent}
          onChange={(e) => {
            setMeetingContent(e.target.value);
            clearError('meetingContent');
          }}
          className={`w-full px-4 py-3 rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none ${
            errors.meetingContent
              ? 'border-red-300 bg-red-50'
              : 'border-gray-200 hover:border-gray-300'
          }`}
          disabled={isRecording || isLoading}
          required
        />
      </div>

      {/* 작성자 */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-gray-700">작성자</label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            placeholder="이름"
            value={writerName}
            onChange={(e) => {
              setWriterName(e.target.value);
              clearError('writerName');
            }}
            className={`px-4 py-3 rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.writerName
                ? 'border-red-300 bg-red-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            disabled={isRecording || isLoading}
            required
          />
          <select
            value={writerPosition}
            onChange={(e) => {
              setWriterPosition(e.target.value);
              clearError('writerPosition');
            }}
            className={`px-4 py-3 rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.writerPosition
                ? 'border-red-300 bg-red-50 text-red-600'
                : 'border-gray-200 hover:border-gray-300 text-gray-700'
            }`}
            disabled={isRecording || isLoading}
            required
          >
            <option value="" disabled>직급 선택</option>
            <option>전임</option>
            <option>선임</option>
            <option>책임</option>
          </select>
          <input
            type="email"
            placeholder="이메일"
            value={writerEmail}
            onChange={(e) => {
              setWriterEmail(e.target.value);
              clearError('writerEmail');
            }}
            className={`px-4 py-3 rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.writerEmail
                ? 'border-red-300 bg-red-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            disabled={isRecording || isLoading}
            required
          />
        </div>
      </div>

      {/* 참석자 */}
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-gray-700">참석자</label>
        <div className="max-h-64 overflow-y-auto space-y-3 p-4 bg-gray-50 rounded-lg border-2 border-gray-200">
          {attendees.map((attendee, index) => (
            <div key={index} className="flex gap-2 items-center bg-white p-3 rounded-lg shadow-sm">
              <input
                type="text"
                placeholder="이름"
                value={attendee.name}
                onChange={(e) => {
                  updateAttendee(index, 'name', e.target.value);
                  clearError(`attendee_${index}`);
                }}
                className="flex-1 px-3 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isRecording || isLoading}
                required
              />
              <select
                value={attendee.position}
                onChange={(e) => {
                  updateAttendee(index, 'position', e.target.value);
                  clearError(`attendee_${index}`);
                }}
                className="flex-1 px-3 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-700"
                disabled={isRecording || isLoading}
                required
              >
                <option value="" disabled>직급</option>
                <option>전임</option>
                <option>선임</option>
                <option>책임</option>
              </select>
              <input
                type="text"
                placeholder="역할"
                value={attendee.authorRole}
                onChange={(e) => {
                  updateAttendee(index, 'authorRole', e.target.value);
                  clearError(`attendee_${index}`);
                }}
                className="flex-1 px-3 py-2 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isRecording || isLoading}
                required
              />
              {index === attendees.length - 1 ? (
                <button
                  type="button"
                  onClick={addAttendee}
                  disabled={isRecording || isLoading}
                  className="w-9 h-9 rounded-full bg-white border-2 border-green-500 text-green-500 font-bold hover:bg-green-50 transition-all duration-200 flex items-center justify-center"
                >
                  +
                </button>
              ) : (
                <button
                  type="button"
                  onClick={() => removeAttendee(index)}
                  disabled={isRecording || isLoading}
                  className="w-9 h-9 rounded-full bg-white border-2 border-red-500 text-red-500 font-bold hover:bg-red-50 transition-all duration-200 flex items-center justify-center"
                >
                  -
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </form>
  );
}

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

export default MeetingForm;
