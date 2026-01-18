import React from 'react';
import { DecisionProblem } from '../../types';

interface DecisionProblemCardProps {
  problems: DecisionProblem[];
}

const FrequencyIndicator: React.FC<{ level: 'low' | 'medium' | 'high' }> = ({ level }) => {
  const count = { low: 1, medium: 2, high: 3 }[level];
  return (
    <div className="flex gap-0.5">
      {[0, 1, 2].map((i) => (
        <div
          key={i}
          className={`w-2 h-2 rounded-full ${
            i < count ? 'bg-rose-400' : 'bg-slate-700'
          }`}
        />
      ))}
    </div>
  );
};

export const DecisionProblemCard: React.FC<DecisionProblemCardProps> = ({ problems }) => {
  return (
    <div className="space-y-3">
      {problems.map((problem, idx) => (
        <div
          key={idx}
          className="bg-slate-800/40 border border-slate-700/50 rounded-2xl p-4 space-y-3"
        >
          {/* 헤더: 문제 유형 + 빈도 */}
          <div className="flex justify-between items-center">
            <h6 className="text-sm font-bold text-white">{problem.problem_type}</h6>
            <div className="flex items-center gap-2">
              <span className="text-[9px] text-slate-500">빈도</span>
              <FrequencyIndicator level={problem.frequency} />
            </div>
          </div>

          {/* 상세 정보 */}
          <div className="space-y-2.5 text-[11px]">
            <div className="flex items-start gap-2">
              <span className="text-rose-400 shrink-0">😰</span>
              <div>
                <span className="text-slate-500 font-medium">심리적 트리거</span>
                <p className="text-slate-200 mt-0.5">{problem.psychological_trigger}</p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <span className="text-blue-400 shrink-0">📍</span>
              <div>
                <span className="text-slate-500 font-medium">발생 상황</span>
                <p className="text-slate-200 mt-0.5">{problem.situation}</p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <span className="text-purple-400 shrink-0">💭</span>
              <div>
                <span className="text-slate-500 font-medium">그 순간의 생각</span>
                <p className="text-slate-200 mt-0.5 italic">"{problem.thought_pattern}"</p>
              </div>
            </div>

            <div className="flex items-start gap-2">
              <span className="text-amber-400 shrink-0">⚡</span>
              <div>
                <span className="text-slate-500 font-medium">결과</span>
                <p className="text-slate-200 mt-0.5">{problem.consequence}</p>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
