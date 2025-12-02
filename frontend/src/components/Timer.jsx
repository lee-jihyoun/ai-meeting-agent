import React, { useState, useEffect } from 'react';

function Timer({ startTime, isRunning }) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!isRunning || !startTime) {
      setElapsed(0);
      return;
    }

    const interval = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [isRunning, startTime]);

  const hours = String(Math.floor(elapsed / 3600)).padStart(2, '0');
  const minutes = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
  const seconds = String(elapsed % 60).padStart(2, '0');

  return (
    <div className="flex flex-col items-center justify-center space-y-3">
      <label className="text-sm font-semibold text-gray-700">경과시간</label>
      <div className={`text-6xl font-bold font-mono transition-all duration-300 ${
        isRunning
          ? 'text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-pink-500 animate-pulse'
          : 'text-gray-400'
      }`}>
        {`${hours}:${minutes}:${seconds}`}
      </div>
      {isRunning && (
        <div className="flex items-center gap-2 text-red-500 text-sm font-semibold">
          <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
          Recording
        </div>
      )}
    </div>
  );
}

export default Timer;
