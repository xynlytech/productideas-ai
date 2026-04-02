import { Suspense } from "react";
import { DashboardClient } from "@/components/dashboard-client";

export default function DashboardPage() {
  return (
    <Suspense
      fallback={
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card animate-pulse h-48" />
          ))}
        </div>
      }
    >
      <DashboardClient />
    </Suspense>
  );
}
