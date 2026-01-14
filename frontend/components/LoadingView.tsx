import React from 'react';

export const LoadingView: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-white p-6">
      <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-8"></div>
      <h2 className="text-2xl font-bold mb-4 animate-pulse text-center">노트를<br/>정리하고 있습니다</h2>
      <p className="text-slate-400 text-center max-w-xs text-sm">기록된 매매 데이터와 시장 상황을 <br/>정밀하게 대조하고 있습니다.</p>
    </div>
  );
};