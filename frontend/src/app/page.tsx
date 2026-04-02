import Link from "next/link";
import { Sparkles, TrendingUp, Search, BarChart3, Zap, Shield, ArrowRight } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface-deepest">
      {/* Nav */}
      <nav className="border-b border-border-subtle">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-brand flex items-center justify-center">
              <Sparkles size={18} className="text-white" />
            </div>
            <span className="font-heading font-semibold text-lg">ProductIdeas</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="text-sm text-text-secondary hover:text-text-primary transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-gradient-cta rounded-xl shadow-glow hover:shadow-glow-lg transition-all"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-accent-blue/10 rounded-full blur-[120px]" />
          <div className="absolute top-1/3 left-1/3 w-[400px] h-[300px] bg-accent-indigo/8 rounded-full blur-[100px]" />
        </div>

        <div className="max-w-6xl mx-auto px-6 pt-24 pb-20 text-center relative">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent-blue/10 border border-accent-blue/20 text-accent-blue text-sm mb-6">
            <Zap size={14} />
            <span>AI-Powered Demand Intelligence</span>
          </div>

          <h1 className="font-heading text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight max-w-4xl mx-auto mb-6 bg-gradient-to-r from-white via-white to-text-secondary bg-clip-text text-transparent">
            Find product ideas people are already searching for
          </h1>

          <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto mb-10">
            Turn Google search signals into scored, validated product opportunities. 
            See demand before you build. Ship what people actually want.
          </p>

          <div className="flex items-center gap-4 justify-center">
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 px-8 py-3.5 text-base font-medium text-white bg-gradient-cta rounded-xl shadow-glow hover:shadow-glow-lg transition-all"
            >
              Explore Ideas
              <ArrowRight size={18} />
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-8 py-3.5 text-base font-medium text-text-secondary border border-border-subtle rounded-xl hover:border-accent-blue/30 hover:text-text-primary transition-all"
            >
              View Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="py-24 border-t border-border-subtle">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="font-heading text-3xl font-bold text-center mb-4">
            Your unfair advantage in product discovery
          </h2>
          <p className="text-text-secondary text-center max-w-xl mx-auto mb-16">
            We analyze millions of search signals to surface real demand — not opinions, not surveys, real searches from real people.
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: Search,
                title: "Search Signal Mining",
                description:
                  "We ingest and analyze Google Trends, autocomplete, and search patterns to detect rising demand signals.",
              },
              {
                icon: BarChart3,
                title: "Opportunity Scoring",
                description:
                  "Every idea is scored on demand growth, competition, pain intensity, and confidence — transparent and evidence-based.",
              },
              {
                icon: TrendingUp,
                title: "Trend Intelligence",
                description:
                  "See what's rising before it peaks. Track momentum, spot emerging niches, and validate ideas with real data.",
              },
            ].map((feature) => (
              <div key={feature.title} className="card">
                <div className="w-10 h-10 rounded-xl bg-accent-blue/10 flex items-center justify-center mb-4">
                  <feature.icon size={20} className="text-accent-blue" />
                </div>
                <h3 className="font-heading font-semibold text-lg mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 bg-surface-deep border-t border-border-subtle">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="font-heading text-3xl font-bold text-center mb-16">
            How it works
          </h2>

          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: "01", title: "Signal Ingestion", desc: "We continuously collect search data from Google Trends and autocomplete." },
              { step: "02", title: "Clustering & Analysis", desc: "Signals are clustered by semantic similarity into topic groups." },
              { step: "03", title: "Scoring", desc: "Each cluster is scored using demand growth, competition, and pain signals." },
              { step: "04", title: "Discover", desc: "Browse ranked opportunities, save favorites, and set alerts." },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="font-mono text-3xl font-bold bg-gradient-brand bg-clip-text text-transparent mb-3">
                  {item.step}
                </div>
                <h3 className="font-heading font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-text-secondary">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 border-t border-border-subtle">
        <div className="max-w-6xl mx-auto px-6 text-center">
          <Shield size={32} className="text-accent-blue mx-auto mb-4" />
          <h2 className="font-heading text-3xl md:text-4xl font-bold mb-4">
            Stop guessing. Start discovering.
          </h2>
          <p className="text-text-secondary max-w-lg mx-auto mb-8">
            Join founders and product teams using real demand data to find their next winning product.
          </p>
          <Link
            href="/signup"
            className="inline-flex items-center gap-2 px-8 py-3.5 text-base font-medium text-white bg-gradient-cta rounded-xl shadow-glow hover:shadow-glow-lg transition-all"
          >
            Explore Ideas
            <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border-subtle py-8">
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between text-sm text-text-muted">
          <span>© 2026 ProductIdeas AI</span>
          <div className="flex gap-6">
            <a href="#" className="hover:text-text-secondary transition-colors">Privacy</a>
            <a href="#" className="hover:text-text-secondary transition-colors">Terms</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
