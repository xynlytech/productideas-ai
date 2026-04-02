import type { ScoreLabel } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ScoreBadgeProps {
  score: number;
  label: ScoreLabel | string | null;
  size?: "sm" | "md";
}

const labelStyles: Record<string, string> = {
  "Very Strong": "score-very-strong",
  Promising: "score-promising",
  "Weak Signal": "score-weak-signal",
  "Low Priority": "score-low-priority",
};

export function ScoreBadge({ score, label, size = "md" }: ScoreBadgeProps) {
  const styleClass = labelStyles[label || ""] || "score-low-priority";

  return (
    <span
      className={cn("score-badge", styleClass, {
        "text-xs px-2 py-0.5": size === "sm",
      })}
    >
      <span className="font-bold">{score.toFixed(0)}</span>
      {label && <span className="opacity-80">· {label}</span>}
    </span>
  );
}
