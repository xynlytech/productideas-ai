"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { User } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Settings, User as UserIcon, CreditCard, Bell as BellIcon, Database, Key } from "lucide-react";

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    api.getMe().then(setUser).catch(() => {});
  }, []);

  const sections = [
    {
      icon: UserIcon,
      title: "Profile",
      content: (
        <div className="space-y-4">
          <div>
            <label className="block text-xs text-text-muted mb-1.5">Name</label>
            <Input defaultValue={user?.name} readOnly />
          </div>
          <div>
            <label className="block text-xs text-text-muted mb-1.5">Email</label>
            <Input defaultValue={user?.email} readOnly />
          </div>
        </div>
      ),
    },
    {
      icon: CreditCard,
      title: "Plan & Subscription",
      content: (
        <div>
          <p className="text-sm text-text-secondary">
            You are on the <span className="text-accent-blue font-medium">Free</span> plan.
          </p>
          <Button variant="secondary" size="sm" className="mt-3">
            Upgrade Plan
          </Button>
        </div>
      ),
    },
    {
      icon: BellIcon,
      title: "Notifications",
      content: (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-text-secondary">Email notifications</span>
            <div className="relative inline-flex h-6 w-11 items-center rounded-full bg-accent-blue">
              <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6" />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm text-text-secondary">Weekly digest</span>
            <div className="relative inline-flex h-6 w-11 items-center rounded-full bg-surface-deep">
              <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-1" />
            </div>
          </div>
        </div>
      ),
    },
    {
      icon: Database,
      title: "Data Preferences",
      content: (
        <div className="space-y-3">
          <div>
            <label className="block text-xs text-text-muted mb-1.5">Default Region</label>
            <select className="w-full bg-surface-deep border border-border-subtle rounded-xl px-4 py-2.5 text-sm text-text-primary focus:outline-none focus:border-accent-blue/40">
              <option value="US">United States</option>
              <option value="GB">United Kingdom</option>
              <option value="DE">Germany</option>
              <option value="CA">Canada</option>
            </select>
          </div>
        </div>
      ),
    },
    {
      icon: Key,
      title: "API Access",
      content: (
        <div>
          <p className="text-sm text-text-muted">
            API access coming soon. You&apos;ll be able to integrate ProductIdeas data into your own workflows.
          </p>
        </div>
      ),
    },
  ];

  return (
    <div className="animate-fade-in max-w-2xl">
      <h1 className="font-heading text-2xl font-bold mb-6">Settings</h1>

      <div className="space-y-4">
        {sections.map((section) => (
          <div key={section.title} className="card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-8 h-8 rounded-lg bg-surface-deep flex items-center justify-center">
                <section.icon size={16} className="text-text-secondary" />
              </div>
              <h2 className="font-heading font-semibold">{section.title}</h2>
            </div>
            {section.content}
          </div>
        ))}
      </div>
    </div>
  );
}
