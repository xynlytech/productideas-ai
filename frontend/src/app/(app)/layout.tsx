import { Sidebar } from "@/components/sidebar";
import { TopBar } from "@/components/top-bar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1 ml-64">
        <TopBar />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
