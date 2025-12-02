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
    <form id="meeting-form-data" onSubmit={handleSubmit}>
      <div className="container">
        <h3><label>회의 제목</label></h3>
        <input
          type="text"
          placeholder="회의 제목을 입력하세요."
          value={meetingTitle}
          onChange={(e) => {
            setMeetingTitle(e.target.value);
            clearError('meetingTitle');
          }}
          className={errors.meetingTitle ? 'invalid' : ''}
          disabled={isRecording || isLoading}
          required
        />
      </div>

      <div className="container">
        <h3><label>회의 내용</label></h3>
        <textarea
          rows="4"
          placeholder="회의 내용을 입력하세요."
          value={meetingContent}
          onChange={(e) => {
            setMeetingContent(e.target.value);
            clearError('meetingContent');
          }}
          className={errors.meetingContent ? 'invalid' : ''}
          disabled={isRecording || isLoading}
          required
        />
      </div>

      <div className="container">
        <h3><label>작성자</label></h3>
        <div className="row">
          <input
            type="text"
            placeholder="이름 입력"
            value={writerName}
            onChange={(e) => {
              setWriterName(e.target.value);
              clearError('writerName');
            }}
            className={errors.writerName ? 'invalid' : ''}
            disabled={isRecording || isLoading}
            required
          />
          <select
            value={writerPosition}
            onChange={(e) => {
              setWriterPosition(e.target.value);
              clearError('writerPosition');
            }}
            className={errors.writerPosition ? 'invalid' : ''}
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
            placeholder="이메일 입력"
            value={writerEmail}
            onChange={(e) => {
              setWriterEmail(e.target.value);
              clearError('writerEmail');
            }}
            className={errors.writerEmail ? 'invalid' : ''}
            disabled={isRecording || isLoading}
            required
          />
        </div>
      </div>

      <div className="container">
        <h3><label className="fixed-label">참석자</label></h3>
        <div className="scroll-container">
          {attendees.map((attendee, index) => (
            <div key={index} className="input-row row">
              <input
                type="text"
                className="name-input"
                placeholder="이름 입력"
                value={attendee.name}
                onChange={(e) => {
                  updateAttendee(index, 'name', e.target.value);
                  clearError(`attendee_${index}`);
                }}
                disabled={isRecording || isLoading}
                required
              />
              <select
                className="position-input"
                value={attendee.position}
                onChange={(e) => {
                  updateAttendee(index, 'position', e.target.value);
                  clearError(`attendee_${index}`);
                }}
                disabled={isRecording || isLoading}
                required
              >
                <option value="" disabled>직급 선택</option>
                <option>전임</option>
                <option>선임</option>
                <option>책임</option>
              </select>
              <input
                type="text"
                className="role-input"
                placeholder="역할 입력"
                value={attendee.authorRole}
                onChange={(e) => {
                  updateAttendee(index, 'authorRole', e.target.value);
                  clearError(`attendee_${index}`);
                }}
                disabled={isRecording || isLoading}
                required
              />
              {index === attendees.length - 1 ? (
                <button
                  type="button"
                  className="fab add-btn"
                  onClick={addAttendee}
                  disabled={isRecording || isLoading}
                >
                  +
                </button>
              ) : (
                <button
                  type="button"
                  className="fab remove-btn"
                  onClick={() => removeAttendee(index)}
                  disabled={isRecording || isLoading}
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
