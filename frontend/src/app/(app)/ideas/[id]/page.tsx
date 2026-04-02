"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { trackEvent } from "@/lib/analytics";
import type { IdeaDetail, IdeaListItem } from "@/lib/types";
import { ScoreBadge } from "@/components/ui/score-badge";
import { TrendIndicator } from "@/components/ui/trend-indicator";
import { IdeaCard } from "@/components/idea-card";
import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  Bookmark,
  Download,
  MapPin,
  Tag,
  TrendingUp,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function IdeaDetailPage() {
  const params = useParams();
  const ideaId = Number(params.id);
  const [idea, setIdea] = useState<IdeaDetail | null>(null);
  const [related, setRelated] = useState<IdeaListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [ideaData, relatedData] = await Promise.all([
          api.getIdea(ideaId),
          api.getRelatedIdeas(ideaId),
        ]);
        setIdea(ideaData);
        setRelated(relatedData);
        trackEvent("idea_viewed", { idea_id: ideaId, score: ideaData.opportunity_score });
      } catch {
        // Handle error
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [ideaId]);

  const handleSave = async () => {
    if (!idea) return;
    if (saved) {
      const allSaved = await api.getSavedIdeas();
      const entry = allSaved.find((s) => s.idea_id === idea.id);
      if (entry) {
        await api.deleteSavedIdea(entry.id);
        setSaved(false);
        trackEvent("idea_unsaved", { idea_id: idea.id });
      }
    } else {
      await api.saveIdea(idea.id);
      setSaved(true);
      trackEvent("idea_saved", { idea_id: idea.id });
    }
  };

  const handleExport = async () => {
    if (!idea) return;
    await api.createExport("csv", { min_score: idea.opportunity_score - 10 });
    trackEvent("export_started", { format: "csv", idea_id: idea.id });
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-surface-raised rounded w-1/3" />
        <div className="h-64 bg-surface-raised rounded-xl" />
      </div>
    );
  }

  if (!idea) {
    return (
      <div className="text-center py-20">
        <p className="text-text-muted text-lg">Idea not found.</p>
        <Link href="/dashboard" className="text-accent-blue text-sm mt-2 inline-block">
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const trendData = idea.trend_data ? JSON.parse(idea.trend_data) : [];

  return (
    <div className="animate-fade-in max-w-6xl">
      {/* Back */}
      <Link
        href="/dashboard"
        className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary mb-6 transition-colors"
      >
        <ArrowLeft size={16} />
        Back to Dashboard
      </Link>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column — Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Header */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              {idea.category && (
                <span className="text-xs text-accent-sky font-medium uppercase tracking-wider">
                  {idea.category}
                </span>
              )}
              <TrendIndicator type={idea.trend_type} />
            </div>
            <h1 className="font-heading text-3xl font-bold mb-2">
              {idea.title}
            </h1>
            <div className="flex items-center gap-4 text-sm text-text-muted">
              {idea.region && (
                <span className="flex items-center gap-1">
                  <MapPin size={14} />
                  {idea.region}
                </span>
              )}
              <span>
                Updated {new Date(idea.updated_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          {/* Problem Statement */}
          {idea.problem_statement && (
            <div className="card">
              <h2 className="font-heading font-semibold text-lg mb-2">
                Problem Statement
              </h2>
              <p className="text-text-secondary leading-relaxed">
                {idea.problem_statement}
              </p>
            </div>
          )}

          {/* Why It Matters */}
          {idea.why_it_matters && (
            <div className="card">
              <h2 className="font-heading font-semibold text-lg mb-2">
                Why It Matters
              </h2>
              <p className="text-text-secondary leading-relaxed">
                {idea.why_it_matters}
              </p>
            </div>
          )}

          {/* Suggested Product */}
          {idea.suggested_product && (
            <div className="card">
              <h2 className="font-heading font-semibold text-lg mb-2">
                Suggested Product Framing
              </h2>
              <p className="text-text-secondary leading-relaxed">
                {idea.suggested_product}
              </p>
            </div>
          )}

          {/* Trend Chart */}
          {trendData.length > 0 && (
            <div className="card">
              <h2 className="font-heading font-semibold text-lg mb-4">
                Search Trend
              </h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData}>
                    <defs>
                      <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="date" stroke="#6F778A" fontSize={12} />
                    <YAxis stroke="#6F778A" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#131C31",
                        border: "1px solid rgba(255,255,255,0.08)",
                        borderRadius: "8px",
                        color: "#fff",
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#3B82F6"
                      strokeWidth={2}
                      fill="url(#trendGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Keywords */}
          {idea.cluster?.label && (
            <div className="card">
              <h2 className="font-heading font-semibold text-lg mb-3">
                Keyword Cluster
              </h2>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-accent-blue/10 text-accent-blue rounded-lg text-sm">
                  <Tag size={14} />
                  {idea.cluster.label}
                </span>
              </div>
            </div>
          )}

          {/* Signals */}
          {idea.signals_summary && (
            <div className="card">
              <h2 className="font-heading font-semibold text-lg mb-3">
                Related Signals
              </h2>
              <div className="flex flex-wrap gap-2">
                {JSON.parse(idea.signals_summary).map((signal: string) => (
                  <span
                    key={signal}
                    className="px-2.5 py-1 bg-surface-deep rounded-lg text-xs text-text-secondary"
                  >
                    {signal}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column — Score & Actions */}
        <div className="space-y-6">
          {/* Score Module */}
          <div className="card sticky top-24">
            <div className="text-center mb-6">
              <div className="font-mono text-5xl font-bold bg-gradient-brand bg-clip-text text-transparent mb-2">
                {idea.opportunity_score.toFixed(0)}
              </div>
              <ScoreBadge
                score={idea.opportunity_score}
                label={idea.score_label}
              />
            </div>

            {/* Score Breakdown */}
            <div className="space-y-3 mb-6">
              {[
                { label: "Demand Growth", value: idea.demand_growth_score, color: "bg-accent-blue" },
                { label: "Pain Intensity", value: idea.pain_intensity_score, color: "bg-accent-indigo" },
                { label: "Competition", value: idea.competition_score, color: "bg-status-warning" },
                { label: "Confidence", value: idea.confidence_score, color: "bg-status-success" },
                { label: "Momentum", value: idea.momentum_score, color: "bg-accent-sky" },
              ].map((metric) => (
                <div key={metric.label}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-text-secondary">{metric.label}</span>
                    <span className="font-mono text-text-primary">
                      {metric.value.toFixed(0)}
                    </span>
                  </div>
                  <div className="h-1.5 bg-surface-deep rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${metric.color}`}
                      style={{ width: `${Math.min(100, metric.value)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="text-xs text-text-muted mb-1">
              <span className="font-mono">Vol:</span> {idea.query_volume.toLocaleString()}
            </div>

            {idea.ranking_reason && (
              <p className="text-xs text-text-muted mt-2">{idea.ranking_reason}</p>
            )}

            {idea.confidence_caveats && (
              <p className="text-xs text-status-warning mt-2">
                ⚠ {idea.confidence_caveats}
              </p>
            )}

            {/* Actions */}
            <div className="flex gap-2 mt-6">
              <Button
                variant={saved ? "primary" : "secondary"}
                className="flex-1"
                onClick={handleSave}
              >
                <Bookmark size={16} fill={saved ? "currentColor" : "none"} />
                {saved ? "Saved" : "Save"}
              </Button>
              <Button
                variant="secondary"
                className="flex-1"
                onClick={handleExport}
              >
                <Download size={16} />
                Export
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Related Ideas */}
      {related.length > 0 && (
        <div className="mt-12">
          <h2 className="font-heading text-xl font-semibold mb-4">
            Related Ideas
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {related.map((r) => (
              <IdeaCard key={r.id} idea={r} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
