import React, { useState } from 'react';

export const DateRangePicker: React.FC<{ 
  value: string, 
  onChange: (val: string) => void 
}> = ({ value, onChange }) => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [range, setRange] = useState<{ start?: Date, end?: Date }>({});
  const [mode, setMode] = useState<'day' | 'yearMonth'>('day');

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const daysInMonth = (year: number, month: number) => new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = (year: number, month: number) => new Date(year, month, 1).getDay();

  const days = daysInMonth(year, month);
  const startDay = firstDayOfMonth(year, month);

  const formatDate = (date: Date) => {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  const handleDateClick = (day: number) => {
    const selected = new Date(year, month, day);
    if (!range.start || (range.start && range.end)) {
      setRange({ start: selected });
    } else if (selected < range.start) {
      setRange({ start: selected });
    } else {
      const newRange = { ...range, end: selected };
      setRange(newRange);
      if (newRange.start && newRange.end) {
        const startStr = formatDate(newRange.start);
        const endStr = formatDate(newRange.end);
        onChange(`${startStr} ~ ${endStr}`);
      }
    }
  };

  const isSelected = (day: number) => {
    const d = new Date(year, month, day);
    if (range.start && d.getTime() === range.start.getTime()) return true;
    if (range.end && d.getTime() === range.end.getTime()) return true;
    return false;
  };

  const isInRange = (day: number) => {
    const d = new Date(year, month, day);
    return range.start && range.end && d > range.start && d < range.end;
  };

  if (mode === 'yearMonth') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 mt-2 select-none animate-in fade-in zoom-in-95 duration-200">
        <div className="flex justify-between items-center mb-4 px-1">
          <button onClick={() => setCurrentDate(new Date(year - 1, month))} className="p-1 hover:bg-slate-800 rounded-md transition-colors text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m15 18-6-6 6-6"/></svg>
          </button>
          <button onClick={() => setMode('day')} className="px-3 py-1 bg-blue-600/10 rounded-full text-[11px] font-black text-blue-400 border border-blue-500/20">
            {year}년
          </button>
          <button onClick={() => setCurrentDate(new Date(year + 1, month))} className="p-1 hover:bg-slate-800 rounded-md transition-colors text-slate-400">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m9 6 6 6-6 6"/></svg>
          </button>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {Array.from({ length: 12 }).map((_, i) => (
            <button
              key={i}
              onClick={() => {
                setCurrentDate(new Date(year, i));
                setMode('day');
              }}
              className={`py-2 text-[10px] font-bold rounded-lg transition-all ${
                i === month ? 'bg-blue-600 text-white' : 'bg-slate-800/50 text-slate-400 hover:bg-slate-800'
              }`}
            >
              {i + 1}월
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 mt-2 select-none animate-in fade-in zoom-in-95 duration-200">
      <div className="flex justify-between items-center mb-4 px-1">
        <button onClick={() => setCurrentDate(new Date(year, month - 1))} className="p-1 hover:bg-slate-800 rounded-md transition-colors text-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <button 
          onClick={() => setMode('yearMonth')}
          className="px-3 py-1 hover:bg-slate-800 rounded-lg transition-all text-[11px] font-black text-white flex items-center gap-1 group"
        >
          {year}년 {month + 1}월
          <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" className="text-blue-500 opacity-50 group-hover:opacity-100 transition-transform"><path d="m6 9 6 6 6-6"/></svg>
        </button>
        <button onClick={() => setCurrentDate(new Date(year, month + 1))} className="p-1 hover:bg-slate-800 rounded-md transition-colors text-slate-400">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m9 6 6 6-6 6"/></svg>
        </button>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center">
        {['일', '월', '화', '수', '목', '금', '토'].map(d => (
          <span key={d} className="text-[9px] font-bold text-slate-600 mb-1">{d}</span>
        ))}
        {Array.from({ length: startDay }).map((_, i) => <div key={`empty-${i}`} />)}
        {Array.from({ length: days }).map((_, i) => {
          const day = i + 1;
          const selected = isSelected(day);
          const inRange = isInRange(day);
          return (
            <button
              key={day}
              onClick={() => handleDateClick(day)}
              className={`text-[10px] h-7 w-7 rounded-lg flex items-center justify-center transition-all ${
                selected ? 'bg-blue-600 text-white font-bold' : 
                inRange ? 'bg-blue-600/20 text-blue-300' : 'hover:bg-slate-800 text-slate-400'
              }`}
            >
              {day}
            </button>
          );
        })}
      </div>
      <div className="mt-3 flex justify-between items-center border-t border-slate-800 pt-3">
        <p className="text-[9px] text-slate-500 font-medium">시작일과 종료일을 선택하세요</p>
        <button onClick={() => { setRange({}); onChange(''); }} className="text-[9px] font-bold text-red-400/70 hover:text-red-400 transition-colors">초기화</button>
      </div>
    </div>
  );
};