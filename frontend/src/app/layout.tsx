import type { Metadata } from "next";
import "./globals.css";
import { AnalyticsProvider } from "@/components/analytics-provider";

export const metadata: Metadata = {
  title: "ProductIdeas AI — Demand Intelligence",
  description:
    "Discover product ideas people are already searching for. AI-powered demand intelligence from search signals.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body>
        <AnalyticsProvider>{children}</AnalyticsProvider>
      </body>
    </html>
  );
}
