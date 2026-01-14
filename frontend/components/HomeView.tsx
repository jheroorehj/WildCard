import React from 'react';
import { ICONS } from '../constants';

interface HomeViewProps {
  startAnalysis: () => void;
  handleQuickAnalysis: () => void;
}

export const HomeView: React.FC<HomeViewProps> = ({ startAnalysis, handleQuickAnalysis }) => {
  return (
    <div className="h-screen max-w-md mx-auto bg-slate-950 text-white flex flex-col relative overflow-hidden">
      <div className="absolute top-[-50px] left-[-50px] w-64 h-64 bg-blue-600/10 blur-[100px] rounded-full pointer-events-none"></div>
      <header className="px-6 pt-6 pb-2 flex justify-between items-center shrink-0 z-20">
        <div className="flex items-center gap-2 group cursor-pointer">
          <div className="w-6 h-6 bg-blue-600 rounded-lg flex items-center justify-center font-black text-[11px] shadow-lg shadow-blue-600/20">W</div>
          <span className="font-black tracking-tighter text-lg leading-none">WILDCARD</span>
        </div>
        <button className="p-2 text-slate-400 hover:text-white transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
        </button>
      </header>
      <main className="flex-1 px-6 overflow-y-auto pb-8">
        <div className="mt-4 space-y-1">
          <h2 className="text-2xl font-bold leading-tight">당신의 <span className="text-blue-500">선택</span>이<br/>최고의 <span className="text-purple-400">자산</span>이 되도록</h2>
          <p className="text-slate-400 text-xs">와일드카드가 당신의 투자 여정을 함께 기록합니다.</p>
        </div>
        <button onClick={startAnalysis} className="mt-6 group relative w-full bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl p-5 flex flex-col justify-between overflow-hidden shadow-2xl shadow-blue-900/40 transition-transform active:scale-[0.98]">
          <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 blur-[30px] rounded-full -mr-12 -mt-12 group-hover:scale-110 transition-transform duration-500"></div>
          <div className="relative z-10 text-left mb-8">
            <span className="bg-white/20 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider">AI : WILDCARD</span>
            <h3 className="text-xl font-black mt-3 tracking-tight">AI 투자 결정 복기 시작</h3>
          </div>
          <div className="relative z-10 flex justify-between items-center">
            <p className="text-blue-100 text-[10px] font-medium opacity-80">포트폴리오 중심의 다중 분석 지원</p>
            <div className="bg-white text-blue-600 p-1.5 rounded-full shadow-lg">{ICONS.ArrowRight}</div>
          </div>
        </button>
        <div className="mt-6 grid grid-cols-2 gap-3">
          <div className="bg-slate-900/50 rounded-2xl p-4">
            <p className="text-slate-500 text-[9px] font-bold uppercase tracking-wider mb-1">나의 분석 노트</p>
            <div className="flex items-baseline gap-1"><span className="text-xl font-bold">12</span><span className="text-slate-400 text-[10px]">건</span></div>
          </div>
          <div className="bg-slate-900/50 rounded-2xl p-4">
            <p className="text-slate-500 text-[9px] font-bold uppercase tracking-wider mb-1">학습 성취도</p>
            <div className="flex items-baseline gap-1"><span className="text-xl font-bold text-green-400">84%</span></div>
          </div>
        </div>
        <div className="mt-8">
          <h4 className="text-xs font-bold text-slate-300 mb-4 flex items-center gap-2"><span className="w-1 h-3 bg-blue-500 rounded-full"></span>최근 복기 노트</h4>
          <div className="space-y-2.5">
            {[{ name: '삼성전자 외 2건', date: '2025.02.10', type: '포트폴리오 분석', onClick: handleQuickAnalysis }, { name: '테슬라', date: '2025.01.24', type: '매매 패턴 분석' }, { name: '엔비디아', date: '2025.01.05', type: '추격 매수 분석' }].map((item, i) => (
              <div key={i} onClick={item.onClick} className="bg-slate-900/30 rounded-xl p-3.5 flex justify-between items-center group hover:bg-slate-900/50 transition-colors cursor-pointer">
                <div><h5 className="font-bold text-sm text-slate-200">{item.name}</h5><p className="text-[9px] text-slate-500">{item.date} • {item.type}</p></div>
                <div className="text-slate-600 group-hover:text-slate-400 transition-colors">{ICONS.ArrowRight}</div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};