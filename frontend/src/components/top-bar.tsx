"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, LogOut, User } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { trackEvent, resetAnalytics } from "@/lib/analytics";

export function TopBar() {
  const [searchQuery, setSearchQuery] = useState("");
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      trackEvent("search_used", { query: searchQuery.trim() });
      router.push(`/dashboard?search=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      trackEvent("logout");
      resetAnalytics();
    } catch {
      // Token already cleared
    }
    router.push("/login");
  };

  return (
    <header className="h-16 bg-surface-deep/80 backdrop-blur-md border-b border-border-subtle flex items-center justify-between px-6 sticky top-0 z-30">
      {/* Search */}
      <form onSubmit={handleSearch} className="flex-1 max-w-lg">
        <div className="relative">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted"
          />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search ideas, categories, keywords..."
            className="pl-9 bg-surface-raised"
          />
        </div>
      </form>

      {/* Actions */}
      <div className="flex items-center gap-3 ml-4">
        <Button variant="ghost" size="sm" className="gap-1.5">
          <User size={16} />
          <span className="hidden sm:inline">Account</span>
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleLogout}
          className="gap-1.5 text-text-muted hover:text-status-error"
        >
          <LogOut size={16} />
        </Button>
      </div>
    </header>
  );
}
