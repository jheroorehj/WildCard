import React from 'react';
import { InvestorCharacter } from '../../types';

interface InvestorPersonaCardProps {
  character: InvestorCharacter;
}

export const InvestorPersonaCard: React.FC<InvestorPersonaCardProps> = ({ character }) => {
  return (
    <div className="space-y-3">
      {/* 캐릭터 타입 */}
      <div className="flex flex-col items-center gap-2">
        <span className="inline-block px-4 py-2 bg-emerald-500/20 border border-emerald-500/40 rounded-2xl text-emerald-300 text-lg font-black tracking-tight">
          {character.type}
        </span>
      </div>

      {/* 설명 */}
      <p className="text-[12px] text-slate-300 leading-relaxed text-center">
        {character.description}
      </p>

      {/* 편향 배지 */}
      <div className="flex justify-center">
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-slate-800/60 rounded-full text-[10px] text-emerald-400/80 font-mono">
          #{character.behavioral_bias}
        </span>
      </div>
    </div>
  );
};
