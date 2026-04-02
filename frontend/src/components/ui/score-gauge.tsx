"use client";

import {
  RadialBarChart,
  RadialBar,
  ResponsiveContainer,
  PolarAngleAxis,
} from "recharts";

interface ScoreGaugeProps {
  score: number;
  size?: number;
}

export function ScoreGauge({ score, size = 120 }: ScoreGaugeProps) {
  const data = [{ value: score, fill: getColor(score) }];

  return (
    <div style={{ width: size, height: size }}>
      <ResponsiveContainer>
        <RadialBarChart
          cx="50%"
          cy="50%"
          innerRadius="70%"
          outerRadius="100%"
          startAngle={180}
          endAngle={0}
          data={data}
        >
          <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
          <RadialBar dataKey="value" cornerRadius={8} background={{ fill: "#0F1626" }} />
        </RadialBarChart>
      </ResponsiveContainer>
    </div>
  );
}

function getColor(score: number): string {
  if (score >= 80) return "#22C55E";
  if (score >= 60) return "#3B82F6";
  if (score >= 40) return "#F59E0B";
  return "#6F778A";
}
