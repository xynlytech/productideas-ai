import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface TrendIndicatorProps {
  type: "rising" | "falling" | "stable" | string | null;
  value?: number;
}

export function TrendIndicator({ type, value }: TrendIndicatorProps) {
  const config = {
    rising: { icon: TrendingUp, className: "trend-up", label: "Rising" },
    falling: { icon: TrendingDown, className: "trend-down", label: "Falling" },
    stable: { icon: Minus, className: "trend-stable", label: "Stable" },
  };

  const { icon: Icon, className, label } = config[type as keyof typeof config] || config.stable;

  return (
    <span className={cn("inline-flex items-center gap-1 text-sm", className)}>
      <Icon size={14} />
      <span>{label}</span>
      {value !== undefined && <span className="font-mono">({value > 0 ? "+" : ""}{value}%)</span>}
    </span>
  );
}
