"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { trackEvent } from "@/lib/analytics";
import type { Alert } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Bell, Plus, Trash2, X } from "lucide-react";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    keyword: "",
    category: "",
    region: "",
    min_score: "",
    cadence: "daily",
  });

  useEffect(() => {
    loadAlerts();
  }, []);

  async function loadAlerts() {
    setLoading(true);
    try {
      setAlerts(await api.getAlerts());
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.createAlert({
      keyword: form.keyword || undefined,
      category: form.category || undefined,
      region: form.region || undefined,
      min_score: form.min_score ? Number(form.min_score) : undefined,
      cadence: form.cadence,
    });
    setForm({ keyword: "", category: "", region: "", min_score: "", cadence: "daily" });
    setShowCreate(false);
    loadAlerts();
    trackEvent("alert_created", { keyword: form.keyword, cadence: form.cadence });
  };

  const handleToggle = async (alert: Alert) => {
    await api.updateAlert(alert.id, { is_active: !alert.is_active });
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === alert.id ? { ...a, is_active: !a.is_active } : a
      )
    );
  };

  const handleDelete = async (id: number) => {
    await api.deleteAlert(id);
    setAlerts((prev) => prev.filter((a) => a.id !== id));
    trackEvent("alert_deleted", { alert_id: id });
  };

  return (
    <div className="animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-heading text-2xl font-bold">Alerts</h1>
          <p className="text-sm text-text-secondary mt-1">
            Get notified when new opportunities match your criteria
          </p>
        </div>
        <Button onClick={() => setShowCreate(true)}>
          <Plus size={16} />
          Create Alert
        </Button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading font-semibold">New Alert</h2>
            <button
              onClick={() => setShowCreate(false)}
              className="text-text-muted hover:text-text-primary"
            >
              <X size={18} />
            </button>
          </div>
          <form onSubmit={handleCreate} className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs text-text-muted mb-1.5">Keyword</label>
              <Input
                value={form.keyword}
                onChange={(e) => setForm((f) => ({ ...f, keyword: e.target.value }))}
                placeholder="e.g. ai productivity"
              />
            </div>
            <div>
              <label className="block text-xs text-text-muted mb-1.5">Category</label>
              <Input
                value={form.category}
                onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
                placeholder="e.g. SaaS"
              />
            </div>
            <div>
              <label className="block text-xs text-text-muted mb-1.5">Region</label>
              <Input
                value={form.region}
                onChange={(e) => setForm((f) => ({ ...f, region: e.target.value }))}
                placeholder="e.g. US"
              />
            </div>
            <div>
              <label className="block text-xs text-text-muted mb-1.5">Min Score</label>
              <Input
                type="number"
                value={form.min_score}
                onChange={(e) => setForm((f) => ({ ...f, min_score: e.target.value }))}
                placeholder="e.g. 60"
                min={0}
                max={100}
              />
            </div>
            <div>
              <label className="block text-xs text-text-muted mb-1.5">Cadence</label>
              <select
                value={form.cadence}
                onChange={(e) => setForm((f) => ({ ...f, cadence: e.target.value }))}
                className="w-full bg-surface-deep border border-border-subtle rounded-xl px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:border-accent-blue/40"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>
            <div className="flex items-end">
              <Button type="submit" className="w-full">
                Create Alert
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Alert List */}
      {loading ? (
        <div className="space-y-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card animate-pulse h-20" />
          ))}
        </div>
      ) : alerts.length > 0 ? (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div key={alert.id} className="card flex items-center gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  {alert.keyword && (
                    <span className="px-2.5 py-0.5 bg-accent-blue/10 text-accent-blue rounded-lg text-sm">
                      {alert.keyword}
                    </span>
                  )}
                  {alert.category && (
                    <span className="px-2.5 py-0.5 bg-accent-indigo/10 text-accent-indigo rounded-lg text-sm">
                      {alert.category}
                    </span>
                  )}
                  {alert.region && (
                    <span className="px-2.5 py-0.5 bg-surface-deep text-text-muted rounded-lg text-sm">
                      {alert.region}
                    </span>
                  )}
                  {alert.min_score && (
                    <span className="text-xs text-text-muted font-mono">
                      ≥{alert.min_score}
                    </span>
                  )}
                </div>
                <div className="text-xs text-text-muted mt-1.5">
                  {alert.cadence} · Created{" "}
                  {new Date(alert.created_at).toLocaleDateString()}
                  {alert.last_triggered_at &&
                    ` · Last triggered ${new Date(alert.last_triggered_at).toLocaleDateString()}`}
                </div>
              </div>

              <div className="flex items-center gap-2 shrink-0">
                <button
                  onClick={() => handleToggle(alert)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    alert.is_active ? "bg-accent-blue" : "bg-surface-deep"
                  }`}
                  role="switch"
                  aria-checked={alert.is_active}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      alert.is_active ? "translate-x-6" : "translate-x-1"
                    }`}
                  />
                </button>
                <button
                  onClick={() => handleDelete(alert.id)}
                  className="p-2 rounded-lg text-text-muted hover:text-status-error hover:bg-status-error/5 transition-colors"
                  aria-label="Delete alert"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20">
          <Bell size={48} className="text-text-muted mx-auto mb-4 opacity-30" />
          <p className="text-text-muted text-lg">No alerts set up yet.</p>
          <p className="text-text-muted text-sm mt-2">
            Create an alert to get notified when opportunities match your criteria.
          </p>
        </div>
      )}
    </div>
  );
}
