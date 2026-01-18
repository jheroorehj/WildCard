import React from 'react';
import { ActionMission } from '../../types';

interface ActionMissionCardProps {
  missions: ActionMission[];
}

const DifficultyBadge: React.FC<{ level: 'easy' | 'medium' | 'hard' }> = ({ level }) => {
  const styles = {
    easy: 'bg-green-500/20 text-green-400 border-green-500/30',
    medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    hard: 'bg-rose-500/20 text-rose-400 border-rose-500/30',
  };
  const labels = { easy: '쉬움', medium: '보통', hard: '어려움' };

  return (
    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold border ${styles[level]}`}>
      난이도 {labels[level]}
    </span>
  );
};

const ImpactBadge: React.FC<{ level: 'low' | 'medium' | 'high' }> = ({ level }) => {
  const styles = {
    low: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
    medium: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    high: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  };
  const labels = { low: '낮음', medium: '보통', high: '높음' };

  return (
    <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold border ${styles[level]}`}>
      효과 {labels[level]}
    </span>
  );
};

export const ActionMissionCard: React.FC<ActionMissionCardProps> = ({ missions }) => {
  // priority 순으로 정렬
  const sortedMissions = [...missions].sort((a, b) => a.priority - b.priority);

  return (
    <div className="space-y-3">
      {sortedMissions.map((mission) => (
        <div
          key={mission.mission_id}
          className="bg-emerald-500/5 border border-emerald-500/30 rounded-2xl p-4 space-y-3"
        >
          {/* 헤더: 우선순위 + 제목 */}
          <div className="flex items-start gap-3">
            <div className="shrink-0 w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <span className="text-emerald-400 text-[10px] font-black">
                #{mission.priority}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <h6 className="text-sm font-bold text-white flex items-center gap-2">
                <span>📋</span>
                {mission.title}
              </h6>
              <p className="text-[11px] text-slate-300 mt-1 leading-relaxed">
                {mission.description}
              </p>
            </div>
          </div>

          {/* 목표 + 기대효과 */}
          <div className="bg-slate-800/40 rounded-xl p-3 space-y-2">
            <div className="flex items-start gap-2 text-[10px]">
              <span className="text-emerald-400">🎯</span>
              <span className="text-slate-400">목표:</span>
              <span className="text-slate-200">{mission.behavioral_target}</span>
            </div>
            <div className="flex items-start gap-2 text-[10px]">
              <span className="text-emerald-400">✨</span>
              <span className="text-slate-400">기대효과:</span>
              <span className="text-slate-200">{mission.expected_outcome}</span>
            </div>
          </div>

          {/* 배지들 */}
          <div className="flex items-center gap-2">
            <DifficultyBadge level={mission.difficulty} />
            <ImpactBadge level={mission.estimated_impact} />
          </div>
        </div>
      ))}
    </div>
  );
};
