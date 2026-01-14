import React from 'react';

export const SplashView: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 transition-opacity duration-700">
      <div className="relative flex items-center justify-center w-40 h-40">
        <div className="absolute inset-0 border-2 border-blue-500/20 rounded-[3rem] animate-[spin_10s_linear_infinite]"></div>
        <div className="absolute inset-4 border border-blue-400/10 rounded-[2.5rem] animate-[spin_15s_linear_infinite_reverse]"></div>
        <div className="z-10 w-28 h-28 bg-blue-600 rounded-[2.2rem] flex items-center justify-center shadow-[0_0_60px_rgba(37,99,235,0.5)] animate-pulse overflow-hidden">
          <span className="text-white text-6xl font-black leading-none select-none tracking-tighter">W</span>
        </div>
      </div>
      <div className="mt-12 text-center space-y-3">
        <h1 className="text-4xl font-black tracking-tighter text-white">WILDCARD</h1>
        <p className="text-blue-400 font-bold tracking-[0.3em] text-[10px] uppercase opacity-80">Loss Analysis Engine</p>
      </div>
      <div className="absolute bottom-12 text-center">
          <p className="text-slate-500 text-sm font-medium animate-bounce">투자 패턴 분석의 새로운 기준</p>
      </div>
    </div>
  );
};