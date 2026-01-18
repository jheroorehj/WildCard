import React from 'react';
import { CognitiveAnalysis } from '../../types';

interface CognitiveBiasCardProps {
  analysis: CognitiveAnalysis;
}

export const CognitiveBiasCard: React.FC<CognitiveBiasCardProps> = ({ analysis }) => {
  const { primary_bias, secondary_biases } = analysis;

  return (
    <div className="space-y-3">
      {/* 주요 편향 */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-[10px] text-amber-400/70 font-bold uppercase tracking-wider">
            주요 편향
          </span>
        </div>
        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-amber-300 font-bold text-sm">{primary_bias.name}</span>
          <span className="text-amber-400/60 text-[10px] font-mono">{primary_bias.english}</span>
        </div>
        <p className="text-[11px] text-slate-300 leading-relaxed mb-2">
          {primary_bias.description}
        </p>
        <div className="flex items-start gap-2 pt-2 border-t border-amber-500/20">
          <span className="text-amber-500 text-[11px]">💥</span>
          <p className="text-[10px] text-amber-400/80 leading-relaxed">
            <span className="font-bold">영향:</span> {primary_bias.impact}
          </p>
        </div>
      </div>

      {/* 보조 편향 */}
      {secondary_biases.length > 0 && (
        <div className="bg-slate-800/40 border border-slate-700/50 rounded-xl p-3 space-y-2">
          <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">
            보조 편향
          </span>
          {secondary_biases.map((bias, idx) => (
            <div key={idx} className="flex items-start gap-2">
              <span className="text-slate-600 mt-0.5">•</span>
              <div>
                <span className="text-slate-300 text-[11px] font-medium">
                  {bias.name}
                </span>
                <span className="text-slate-500 text-[10px] ml-1.5">
                  ({bias.english})
                </span>
                <p className="text-[10px] text-slate-400 mt-0.5">
                  {bias.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
