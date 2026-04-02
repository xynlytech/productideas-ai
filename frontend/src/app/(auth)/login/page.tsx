"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { trackEvent } from "@/lib/analytics";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Sparkles } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.login(email, password);
      trackEvent("login");
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="text-center mb-8">
        <div className="w-12 h-12 rounded-xl bg-gradient-brand flex items-center justify-center mx-auto mb-4">
          <Sparkles size={24} className="text-white" />
        </div>
        <h1 className="font-heading text-2xl font-bold">Welcome back</h1>
        <p className="text-sm text-text-secondary mt-1">
          Sign in to your account
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="bg-status-error/10 border border-status-error/20 rounded-xl px-4 py-3 text-sm text-status-error">
            {error}
          </div>
        )}

        <div>
          <label className="block text-xs text-text-muted mb-1.5">Email</label>
          <Input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            autoFocus
          />
        </div>

        <div>
          <label className="block text-xs text-text-muted mb-1.5">Password</label>
          <Input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />
        </div>

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Signing in..." : "Sign In"}
        </Button>
      </form>

      <p className="text-center text-sm text-text-muted mt-6">
        Don&apos;t have an account?{" "}
        <Link href="/signup" className="text-accent-blue hover:underline">
          Sign up
        </Link>
      </p>
    </div>
  );
}
