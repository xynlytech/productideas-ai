"use client";

import { useEffect, useState, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import { trackEvent } from "@/lib/analytics";
import type { PaginatedIdeas, IdeasFilters } from "@/lib/types";
import { IdeaCard } from "@/components/idea-card";
import { FilterChip } from "@/components/ui/filter-chip";
import { Button } from "@/components/ui/button";
import { BarChart3, Grid3X3, List } from "lucide-react";

const CATEGORIES = ["SaaS", "E-commerce", "Health & Wellness", "Education", "Finance", "Productivity"];
const SORT_OPTIONS = [
  { value: "score", label: "Score" },
  { value: "recency", label: "Recent" },
  { value: "growth", label: "Growth" },
  { value: "confidence", label: "Confidence" },
  { value: "momentum", label: "Momentum" },
] as const;

export function DashboardClient() {
  const searchParams = useSearchParams();
  const [data, setData] = useState<PaginatedIdeas | null>(null);
  const [loading, setLoading] = useState(true);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [filters, setFilters] = useState<IdeasFilters>({
    search: searchParams.get("search") || undefined,
    sort: "score",
    order: "desc",
    page: 1,
    limit: 20,
  });

  const fetchIdeas = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.getIdeas(filters);
      setData(result);
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchIdeas();
  }, [fetchIdeas]);

  useEffect(() => {
    api
      .getSavedIdeas()
      .then((saved) => {
        setSavedIds(new Set(saved.map((s) => s.idea_id)));
      })
      .catch(() => {});
  }, []);

  const handleSave = async (ideaId: number) => {
    if (savedIds.has(ideaId)) {
      const saved = await api.getSavedIdeas();
      const entry = saved.find((s) => s.idea_id === ideaId);
      if (entry) {
        await api.deleteSavedIdea(entry.id);
        setSavedIds((prev) => {
          const next = new Set(prev);
          next.delete(ideaId);
          return next;
        });
        trackEvent("idea_unsaved", { idea_id: ideaId });
      }
    } else {
      await api.saveIdea(ideaId);
      setSavedIds((prev) => new Set(prev).add(ideaId));
      trackEvent("idea_saved", { idea_id: ideaId });
    }
  };

  const toggleCategory = (cat: string) => {
    setFilters((prev) => ({
      ...prev,
      category: prev.category === cat ? undefined : cat,
      page: 1,
    }));
    trackEvent("filter_used", { filter: "category", value: cat });
  };

  return (
    <div className="animate-fade-in">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="font-heading text-2xl font-bold">Dashboard</h1>
          <p className="mt-1 text-sm text-text-secondary">{data ? `${data.total} opportunities found` : "Loading..."}</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode("grid")}
            className={`rounded-lg p-2 transition-colors ${
              viewMode === "grid" ? "bg-surface-raised text-text-primary" : "text-text-muted hover:text-text-primary"
            }`}
            aria-label="Grid view"
          >
            <Grid3X3 size={18} />
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`rounded-lg p-2 transition-colors ${
              viewMode === "list" ? "bg-surface-raised text-text-primary" : "text-text-muted hover:text-text-primary"
            }`}
            aria-label="List view"
          >
            <List size={18} />
          </button>
        </div>
      </div>

      {data && (
        <div className="mb-6 grid grid-cols-3 gap-4">
          <div className="card flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent-blue/10">
              <BarChart3 size={18} className="text-accent-blue" />
            </div>
            <div>
              <p className="text-xs text-text-muted">Total Ideas</p>
              <p className="font-mono font-semibold">{data.total}</p>
            </div>
          </div>
          <div className="card flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-status-success/10">
              <BarChart3 size={18} className="text-status-success" />
            </div>
            <div>
              <p className="text-xs text-text-muted">Avg Score</p>
              <p className="font-mono font-semibold">
                {data.items.length > 0
                  ? (data.items.reduce((sum, i) => sum + i.opportunity_score, 0) / data.items.length).toFixed(1)
                  : "-"}
              </p>
            </div>
          </div>
          <div className="card flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-accent-indigo/10">
              <BarChart3 size={18} className="text-accent-indigo" />
            </div>
            <div>
              <p className="text-xs text-text-muted">Saved</p>
              <p className="font-mono font-semibold">{savedIds.size}</p>
            </div>
          </div>
        </div>
      )}

      <div className="mb-6 flex flex-wrap items-center gap-2">
        {CATEGORIES.map((cat) => (
          <FilterChip
            key={cat}
            label={cat}
            active={filters.category === cat}
            onClick={() => toggleCategory(cat)}
            onRemove={() => toggleCategory(cat)}
          />
        ))}

        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-text-muted">Sort:</span>
          <select
            value={filters.sort}
            onChange={(e) => {
              const val = e.target.value as IdeasFilters["sort"];
              setFilters((prev) => ({ ...prev, sort: val, page: 1 }));
              trackEvent("sort_changed", { sort: val });
            }}
            className="rounded-lg border border-border-subtle bg-surface-raised px-3 py-1.5 text-sm text-text-secondary focus:border-accent-blue/40 focus:outline-none"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card h-48 animate-pulse" />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className={viewMode === "grid" ? "grid gap-4 md:grid-cols-2 lg:grid-cols-3" : "flex flex-col gap-3"}>
            {data.items.map((idea) => (
              <IdeaCard key={idea.id} idea={idea} onSave={handleSave} isSaved={savedIds.has(idea.id)} />
            ))}
          </div>

          {data.pages > 1 && (
            <div className="mt-8 flex items-center justify-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                disabled={data.page <= 1}
                onClick={() => setFilters((prev) => ({ ...prev, page: (prev.page || 1) - 1 }))}
              >
                Previous
              </Button>
              <span className="px-3 text-sm text-text-secondary">
                Page {data.page} of {data.pages}
              </span>
              <Button
                variant="secondary"
                size="sm"
                disabled={data.page >= data.pages}
                onClick={() => setFilters((prev) => ({ ...prev, page: (prev.page || 1) + 1 }))}
              >
                Next
              </Button>
            </div>
          )}
        </>
      ) : (
        <div className="py-20 text-center">
          <p className="text-lg text-text-muted">No ideas found for this query.</p>
          <p className="mt-2 text-sm text-text-muted">Try adjusting your filters or search terms.</p>
        </div>
      )}
    </div>
  );
}
