import React from 'react';
import { ProfileMetrics } from '../../types';

interface RadarChartProps {
  metrics: ProfileMetrics;
}

const METRIC_KEYS = [
  'information_sensitivity',
  'analysis_depth',
  'risk_management',
  'decisiveness',
  'emotional_control',
  'learning_adaptability',
] as const;

// 육각형 꼭지점 계산 (12시 방향부터 시계방향)
const getHexagonPoint = (centerX: number, centerY: number, radius: number, index: number): { x: number; y: number } => {
  const angle = (Math.PI / 2) + (2 * Math.PI * index) / 6;
  return {
    x: centerX + radius * Math.cos(angle),
    y: centerY - radius * Math.sin(angle),
  };
};

const getHexagonPoints = (centerX: number, centerY: number, radius: number): string => {
  return METRIC_KEYS.map((_, i) => {
    const point = getHexagonPoint(centerX, centerY, radius, i);
    return `${point.x},${point.y}`;
  }).join(' ');
};

export const RadarChart: React.FC<RadarChartProps> = ({ metrics }) => {
  const centerX = 120;
  const centerY = 120;
  const maxRadius = 80;

  // 점수를 반지름으로 변환
  const getDataPoints = (): string => {
    return METRIC_KEYS.map((key, i) => {
      const score = metrics[key]?.score ?? 50;
      const radius = (score / 100) * maxRadius;
      const point = getHexagonPoint(centerX, centerY, radius, i);
      return `${point.x},${point.y}`;
    }).join(' ');
  };

  // 점수별 색상 반환
  const getScoreColor = (score: number): string => {
    if (score <= 40) return '#f43f5e'; // rose-500
    if (score <= 60) return '#f59e0b'; // amber-500
    return '#10b981'; // emerald-500
  };

  // 라벨 위치 계산 (바깥쪽)
  const getLabelPosition = (index: number): { x: number; y: number; anchor: string } => {
    const point = getHexagonPoint(centerX, centerY, maxRadius + 25, index);
    let anchor = 'middle';
    if (index === 1 || index === 2) anchor = 'start';
    if (index === 4 || index === 5) anchor = 'end';
    return { ...point, anchor };
  };

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 240 240" className="w-64 h-64">
        {/* 배경 그리드 (20%, 40%, 60%, 80%, 100%) */}
        {[0.2, 0.4, 0.6, 0.8, 1].map((scale) => (
          <polygon
            key={scale}
            points={getHexagonPoints(centerX, centerY, maxRadius * scale)}
            className="fill-none stroke-slate-700/50"
            strokeWidth="0.5"
          />
        ))}

        {/* 축 라인 */}
        {METRIC_KEYS.map((_, i) => {
          const point = getHexagonPoint(centerX, centerY, maxRadius, i);
          return (
            <line
              key={i}
              x1={centerX}
              y1={centerY}
              x2={point.x}
              y2={point.y}
              className="stroke-slate-700/30"
              strokeWidth="0.5"
            />
          );
        })}

        {/* 취약 구간 하이라이트 (40점 이하 영역) */}
        <polygon
          points={getHexagonPoints(centerX, centerY, maxRadius * 0.4)}
          className="fill-rose-500/5 stroke-none"
        />

        {/* 데이터 영역 */}
        <polygon
          points={getDataPoints()}
          className="fill-emerald-500/20 stroke-emerald-400"
          strokeWidth="2"
          style={{
            animation: 'radarExpand 0.8s ease-out forwards',
            transformOrigin: 'center',
          }}
        />

        {/* 각 축의 데이터 포인트 */}
        {METRIC_KEYS.map((key, i) => {
          const score = metrics[key]?.score ?? 50;
          const radius = (score / 100) * maxRadius;
          const point = getHexagonPoint(centerX, centerY, radius, i);
          const isWeak = score <= 40;

          return (
            <g key={key}>
              {/* 점수 원형 마커 */}
              <circle
                cx={point.x}
                cy={point.y}
                r={isWeak ? 5 : 4}
                fill={getScoreColor(score)}
                className={isWeak ? 'animate-pulse' : ''}
              />
            </g>
          );
        })}

        {/* 라벨 + 점수 (경고 아이콘 포함) */}
        {METRIC_KEYS.map((key, i) => {
          const metric = metrics[key];
          const score = metric?.score ?? 50;
          const label = metric?.label || key;
          const pos = getLabelPosition(i);
          const isWeak = score <= 40;

          return (
            <g key={`label-${key}`}>
              <text
                x={pos.x}
                y={pos.y - 6}
                textAnchor={pos.anchor}
                className="text-[9px] font-medium"
                fill={isWeak ? '#f43f5e' : '#94a3b8'}
              >
                {label}
              </text>
              {/* 점수 + 경고 아이콘 */}
              <text
                x={pos.x}
                y={pos.y + 6}
                textAnchor={pos.anchor}
                className="text-[11px] font-bold"
                fill={getScoreColor(score)}
              >
                {isWeak ? `⚠️ ${score}` : score}
              </text>
            </g>
          );
        })}
      </svg>

      {/* 범례 */}
      <div className="flex justify-center gap-4 mt-2 text-[10px]">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-rose-500" /> 취약
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-amber-500" /> 주의
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-emerald-500" /> 양호
        </span>
      </div>

      <style>{`
        @keyframes radarExpand {
          from {
            transform: scale(0);
            opacity: 0;
          }
          to {
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};
