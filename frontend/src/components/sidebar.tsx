"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Lightbulb,
  Bookmark,
  Bell,
  Settings,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/saved", label: "Saved Ideas", icon: Bookmark },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 bottom-0 w-64 bg-surface-deep border-r border-border-subtle flex flex-col z-40">
      {/* Logo */}
      <div className="h-16 flex items-center gap-2.5 px-6 border-b border-border-subtle">
        <div className="w-8 h-8 rounded-lg bg-gradient-brand flex items-center justify-center">
          <Sparkles size={18} className="text-white" />
        </div>
        <span className="font-heading font-semibold text-lg text-text-primary">
          ProductIdeas
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-colors",
                isActive
                  ? "bg-accent-blue/10 text-accent-blue font-medium"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-raised"
              )}
            >
              <item.icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="p-4 border-t border-border-subtle">
        <div className="bg-surface-raised rounded-xl p-3 text-center">
          <Lightbulb size={20} className="text-accent-sky mx-auto mb-1.5" />
          <p className="text-xs text-text-secondary">
            Discover trending product opportunities daily
          </p>
        </div>
      </div>
    </aside>
  );
}
