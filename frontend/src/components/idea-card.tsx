"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import type { IdeaListItem } from "@/lib/types";
import { ScoreBadge } from "@/components/ui/score-badge";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { Bookmark } from "lucide-react";

interface IdeaCardProps {
  idea: IdeaListItem;
  onSave?: (id: number) => void;
  isSaved?: boolean;
}

export function IdeaCard({ idea, onSave, isSaved }: IdeaCardProps) {
  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
    >
      <Link
        href={`/ideas/${idea.id}`}
        className="card block group cursor-pointer"
      >
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              {idea.category && (
                <span className="text-xs text-accent-sky font-medium uppercase tracking-wider">
                  {idea.category}
                </span>
              )}
              {idea.region && (
                <span className="text-xs text-text-muted">
                  {idea.region}
                </span>
              )}
            </div>
            <h3 className="font-heading font-semibold text-text-primary group-hover:text-accent-blue transition-colors line-clamp-2">
              {idea.title}
            </h3>
          </div>

          <div className="flex flex-col items-end gap-2 shrink-0">
            <ScoreBadge
              score={idea.opportunity_score}
              label={idea.score_label}
              size="sm"
            />
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onSave?.(idea.id);
              }}
              className={`p-1.5 rounded-lg transition-colors ${
                isSaved
                  ? "text-accent-blue bg-accent-blue/10"
                  : "text-text-muted hover:text-accent-blue hover:bg-accent-blue/5"
              }`}
              aria-label={isSaved ? "Unsave idea" : "Save idea"}
            >
              <Bookmark size={16} fill={isSaved ? "currentColor" : "none"} />
            </button>
          </div>
        </div>

        {idea.problem_statement && (
          <p className="text-sm text-text-secondary line-clamp-2 mb-3">
            {idea.problem_statement}
          </p>
        )}

        <div className="flex items-center gap-4 text-xs text-text-muted">
          <TrendIndicator type={idea.trend_type} />
          <span className="font-mono">
            Vol: {idea.query_volume.toLocaleString()}
          </span>
          <span className="font-mono">
            Conf: {idea.confidence_score.toFixed(0)}%
          </span>
        </div>
      </Link>
    </motion.div>
  );
}
