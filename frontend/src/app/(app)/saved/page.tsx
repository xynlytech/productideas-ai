"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { SavedIdea } from "@/lib/types";
import { ScoreBadge } from "@/components/ui/score-badge";
import { Button } from "@/components/ui/button";
import { Bookmark, Pencil, Trash2, FileText } from "lucide-react";
import Link from "next/link";

type Tab = "all" | "high" | "recent";

export default function SavedIdeasPage() {
  const [saved, setSaved] = useState<SavedIdea[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<Tab>("all");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editNote, setEditNote] = useState("");

  useEffect(() => {
    loadSaved();
  }, []);

  async function loadSaved() {
    setLoading(true);
    try {
      const data = await api.getSavedIdeas();
      setSaved(data);
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  }

  const filteredItems = saved.filter((item) => {
    if (activeTab === "high") return (item.idea?.opportunity_score || 0) >= 70;
    if (activeTab === "recent") {
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return new Date(item.created_at) >= weekAgo;
    }
    return true;
  });

  const handleDelete = async (id: number) => {
    await api.deleteSavedIdea(id);
    setSaved((prev) => prev.filter((s) => s.id !== id));
  };

  const handleUpdateNote = async (id: number) => {
    await api.updateSavedIdea(id, editNote);
    setSaved((prev) =>
      prev.map((s) => (s.id === id ? { ...s, note: editNote } : s))
    );
    setEditingId(null);
    setEditNote("");
  };

  const tabs: { key: Tab; label: string }[] = [
    { key: "all", label: "All" },
    { key: "high", label: "High Score" },
    { key: "recent", label: "Recent" },
  ];

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-bold">Saved Ideas</h1>
          <p className="text-sm text-text-secondary mt-1">
            {saved.length} ideas saved
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-surface-deep rounded-xl p-1 w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
              activeTab === tab.key
                ? "bg-surface-raised text-text-primary font-medium"
                : "text-text-muted hover:text-text-secondary"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* List */}
      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card animate-pulse h-24" />
          ))}
        </div>
      ) : filteredItems.length > 0 ? (
        <div className="space-y-3">
          {filteredItems.map((item) => (
            <div key={item.id} className="card flex items-start gap-4">
              <div className="flex-1 min-w-0">
                <Link
                  href={`/ideas/${item.idea_id}`}
                  className="font-heading font-semibold text-text-primary hover:text-accent-blue transition-colors"
                >
                  {item.idea?.title || `Idea #${item.idea_id}`}
                </Link>

                <div className="flex items-center gap-3 mt-1.5 text-sm">
                  {item.idea && (
                    <ScoreBadge
                      score={item.idea.opportunity_score}
                      label={item.idea.score_label}
                      size="sm"
                    />
                  )}
                  {item.idea?.category && (
                    <span className="text-text-muted">{item.idea.category}</span>
                  )}
                  <span className="text-text-muted">
                    Saved {new Date(item.created_at).toLocaleDateString()}
                  </span>
                </div>

                {/* Note */}
                {editingId === item.id ? (
                  <div className="mt-3 flex gap-2">
                    <input
                      value={editNote}
                      onChange={(e) => setEditNote(e.target.value)}
                      className="flex-1 bg-surface-deep border border-border-subtle rounded-lg px-3 py-1.5 text-sm text-text-primary focus:outline-none focus:border-accent-blue/40"
                      placeholder="Add a note..."
                      autoFocus
                    />
                    <Button
                      size="sm"
                      onClick={() => handleUpdateNote(item.id)}
                    >
                      Save
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setEditingId(null)}
                    >
                      Cancel
                    </Button>
                  </div>
                ) : item.note ? (
                  <div className="mt-2 flex items-start gap-2">
                    <FileText size={14} className="text-text-muted mt-0.5 shrink-0" />
                    <p className="text-sm text-text-muted">{item.note}</p>
                  </div>
                ) : null}
              </div>

              <div className="flex items-center gap-1 shrink-0">
                <button
                  onClick={() => {
                    setEditingId(item.id);
                    setEditNote(item.note || "");
                  }}
                  className="p-2 rounded-lg text-text-muted hover:text-text-primary hover:bg-surface-deep transition-colors"
                  aria-label="Edit note"
                >
                  <Pencil size={14} />
                </button>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="p-2 rounded-lg text-text-muted hover:text-status-error hover:bg-status-error/5 transition-colors"
                  aria-label="Remove saved idea"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <Bookmark size={48} className="text-text-muted mx-auto mb-4 opacity-30" />
          <p className="text-text-muted text-lg">No saved ideas yet.</p>
          <p className="text-text-muted text-sm mt-2">
            Start exploring opportunities and save the ones that catch your eye.
          </p>
          <Link href="/dashboard">
            <Button variant="secondary" className="mt-4">
              Explore Ideas
            </Button>
          </Link>
        </div>
      )}
    </div>
  );
}
