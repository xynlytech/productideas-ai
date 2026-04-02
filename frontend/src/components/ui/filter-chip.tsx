import { cn } from "@/lib/utils";

interface FilterChipProps {
  label: string;
  active?: boolean;
  onClick?: () => void;
  onRemove?: () => void;
}

export function FilterChip({ label, active, onClick, onRemove }: FilterChipProps) {
  return (
    <button
      onClick={onClick}
      className={cn("filter-chip", active && "filter-chip-active")}
    >
      <span>{label}</span>
      {active && onRemove && (
        <span
          role="button"
          tabIndex={0}
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.stopPropagation();
              onRemove?.();
            }
          }}
          className="ml-1 text-text-muted hover:text-text-primary"
        >
          ×
        </span>
      )}
    </button>
  );
}
