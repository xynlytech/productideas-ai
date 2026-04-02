# Plan: ProductIdeas AI — Full Implementation Plan

## TL;DR
Build a premium demand intelligence SaaS (Next.js + FastAPI + PostgreSQL) that discovers product opportunities from search signals. Dark-first, data-rich UI. Modular monolith backend with ingestion → normalization → clustering → scoring pipeline. MVP ships with Google Trends + Autocomplete as data sources. Phased rollout across 6 phases.

---

## Phase 1: Foundation & Infrastructure Setup
*Duration goal: Establish all scaffolding before any feature work*

### Step 1.1 — Repository & Monorepo Setup
- Create GitHub monorepo with `/frontend` (Next.js App Router + TypeScript) and `/backend` (Python FastAPI)
- Configure Prettier + ESLint for frontend, Ruff + Black + pytest for backend
- Add Docker Compose for local dev (PostgreSQL, Redis, backend, frontend)
- Set up `.env.example` files for both services

### Step 1.2 — CI/CD Pipeline (*parallel with 1.1*)
- GitHub Actions workflow: lint → test → build for both frontend and backend
- Preview deploys on Vercel for frontend PRs
- Backend deploy pipeline targeting Render/Railway/Fly.io

### Step 1.3 — Database & Migrations (*depends on 1.1*)
- Set up PostgreSQL (Neon or Supabase for managed)
- Initialize Alembic for migrations
- Create initial migration with all core entities from PRD §15:
  - `users`, `topic_clusters`, `cluster_keywords`, `opportunity_ideas`, `source_signals`, `saved_ideas`, `alerts`, `exports`, `audit_logs`
- Set up Redis (Upstash) for caching and job queues
- Set up S3-compatible storage for exports/snapshots

### Step 1.4 — Authentication (*depends on 1.3*)
- Integrate Auth.js or Clerk for auth
- Implement `POST /auth/signup`, `POST /auth/login`, `POST /auth/logout`
- Set up secure session/token handling
- Add role-based access control (user vs admin)
- Rate limiting on public auth endpoints

**Verification:**
- `docker-compose up` runs all services locally
- CI pipeline passes on empty repo
- Auth signup → login → logout flow works end-to-end
- Database migrations run cleanly

---

## Phase 2: Data Pipeline (Backend Core)
*The intelligence engine — this is the product's moat*

### Step 2.1 — Ingestion Layer
- Build source connector interface (abstract base class)
- Implement Google Trends connector with rate-limit handling, retries, source health monitoring
- Implement Google Autocomplete connector
- Create scheduled job system using Celery/RQ with cron-based triggers
- Store raw signals in `source_signals` table with `payload_ref` to S3

### Step 2.2 — Cleaning & Normalization (*depends on 2.1*)
- Lowercase and standardize text
- Remove duplicates (exact + fuzzy)
- Normalize timestamps and geo labels
- Language detection (filter to supported languages)
- Spam/junk pattern removal via regex filters

### Step 2.3 — Clustering (*depends on 2.2*)
- Hybrid clustering: sentence-transformer embeddings + rule-based grouping
- Group semantically related queries into `topic_clusters`
- Assign cluster labels and `cluster_keywords` with weights
- Identify problem themes per cluster

### Step 2.4 — Scoring Engine (*depends on 2.3*)
- Implement deterministic scoring formula:
  `Opportunity Score = ((Demand Growth × Query Volume × Pain Intensity × Momentum) / Competition Saturation) × Confidence Multiplier`
- Compute sub-scores: demand_growth_score, competition_score, pain_intensity_score, confidence_score
- Normalize to 0–100, label as Very Strong / Promising / Weak Signal / Low Priority
- Store scored results in `opportunity_ideas` table
- Each score must expose components, contributing signals, ranking reason, confidence caveats

### Step 2.5 — Pipeline Orchestration (*depends on 2.1–2.4*)
- Wire full pipeline: Ingestion → Normalization → Clustering → Scoring
- Add admin endpoints:
  - `POST /admin/ingestion/run` — trigger ingestion
  - `POST /admin/scoring/rebuild` — recompute scores
  - `GET /admin/sources` — view source health
- Add job observability (duration, success rate, error logging)

**Verification:**
- Run full pipeline with Google Trends + Autocomplete data
- Verify scored ideas appear in `opportunity_ideas` with all sub-scores
- Admin endpoints trigger and report correctly
- Source failures don't crash the pipeline (graceful degradation)

---

## Phase 3: Core API Layer
*Expose pipeline results to frontend*

### Step 3.1 — Ideas API (*depends on Phase 2*)
- `GET /ideas` — ranked list with filters (category, region, min_score, max_score, trend_type, confidence_min, competition_max, sort, page, limit)
- `GET /ideas/{id}` — full detail with score breakdown, trend data, keyword clusters, problem statement, suggested solution
- `GET /ideas/{id}/related` — related ideas from same/adjacent clusters
- Pagination, input validation (Pydantic), caching via Redis

### Step 3.2 — Clusters API (*parallel with 3.1*)
- `GET /clusters` — list topic clusters
- `GET /clusters/{id}` — detailed cluster view with keywords

### Step 3.3 — Saved Ideas API (*parallel with 3.1*)
- `GET /saved-ideas` — user's bookmarked ideas
- `POST /saved-ideas` — save an idea with optional note
- `PATCH /saved-ideas/{id}` — update note
- `DELETE /saved-ideas/{id}` — remove bookmark
- All scoped to authenticated user only

### Step 3.4 — Alerts API (*parallel with 3.1*)
- `GET /alerts` — list user alerts
- `POST /alerts` — create alert (keyword, category, score threshold, region, cadence)
- `PATCH /alerts/{id}` — update alert
- `DELETE /alerts/{id}` — delete alert
- Background job to evaluate alerts against new ideas and flag triggered alerts

### Step 3.5 — Export API (*parallel with 3.1*)
- `POST /exports` — generate CSV/PDF export (async job)
- `GET /exports/{id}` — get export status and download URL
- Store generated files in S3

### Step 3.6 — Search (*depends on 3.1*)
- PostgreSQL full-text search on idea titles, problem statements, keywords
- Integrated into `GET /ideas` via search query param

**Verification:**
- API tests for every endpoint (happy path + edge cases + auth)
- Pagination returns correct pages
- Filters narrow results correctly
- Saved ideas persist across sessions
- Export generates valid CSV/PDF

---

## Phase 4: Design System & Frontend Foundation
*Can start in parallel with Phase 2–3 for UI scaffolding*

### Step 4.1 — Design System / Component Library
- Configure Tailwind CSS with brand color tokens from Brand Guidelines §7 and UI/UX Prompt §3:
  - Backgrounds: #05070D, #0A0F1A, #0F1626, #131C31
  - Accents: #3B82F6, #38BDF8, #6366F1, #7C3AED
  - Text: #FFFFFF, #A1AABF, #6F778A
  - Status: #22C55E, #F59E0B, #EF4444
  - Border: rgba(255,255,255,0.08)
  - Gradient: linear-gradient(135deg, #3B82F6, #38BDF8, #6366F1)
- Set up typography: Space Grotesk (headings), Inter (body), IBM Plex Mono (data/metrics)
- Build reusable components using shadcn/ui primitives:
  - **Sidebar** — dark vertical, logo top, nav items with icons, active state with tinted bg + left accent bar
  - **Top Bar** — search input, filter chips, quick actions
  - **Idea Card** — title, score badge (pill, bold, color-coded), problem summary, trend indicator (arrow + %), category tag, region tag, confidence label, save icon
  - **Score Badge** — rounded pill, bold number, distinct color by tier (Very Strong/Promising/Weak/Low)
  - **Filter Chips** — pill-shaped, minimal border, active = filled, hover = elevated
  - **Trend Indicator** — arrow + percentage, optional sparkline, color-coded
  - **Buttons** — primary (gradient + glow), secondary (surface tone), ghost (text-only/light border)
- Configure Framer Motion for interactions:
  - Hover: slight lift + soft glow
  - Card selection: stronger border + glow
  - CTA: gradient with stronger shadow
  - Filter chips: smooth state change
  - Search focus: subtle accent border

### Step 4.2 — App Shell & Routing (*depends on 4.1*)
- Next.js App Router layout with sidebar + top bar
- Routes: `/`, `/dashboard`, `/ideas/[id]`, `/saved`, `/alerts`, `/settings`
- Auth middleware (redirect unauthenticated users)
- Dark mode as default and only mode

**Verification:**
- Component storybook or visual review of all base components
- Color tokens match brand guidelines exactly
- Typography hierarchy renders correctly at all specified sizes
- App shell renders sidebar + top bar + content area

---

## Phase 5: Frontend Pages (Feature UI)
*Depends on Phase 3 (API) and Phase 4 (design system)*

### Step 5.1 — Dashboard Page
- Search bar with filter chips below
- Ranked opportunity card grid/list (switchable)
- Sort controls: score, recency, growth, confidence
- Filter panel: category, region, score range, trend type, confidence, competition
- Summary stats bar (total ideas, avg score, top category)
- Infinite scroll or pagination
- Save idea directly from card
- Empty state: "No ideas found for this query."

### Step 5.2 — Idea Detail Page (*parallel with 5.1*)
- Two-column layout
- Left: problem statement, why it matters, suggested product framing, trend chart (Recharts/Visx), keyword cluster tags, related signals
- Right: opportunity score module with breakdown (demand growth, pain intensity, competition, confidence), region, category, save button, export button
- Related ideas section at bottom
- Visual hierarchy: score → title → trend → description → metadata

### Step 5.3 — Saved Ideas Page (*parallel with 5.1*)
- Header + tabs: All, High Score, Recent
- Saved idea cards with note preview, date saved
- Edit note inline, remove saved idea
- Empty state: "No saved ideas yet. Start exploring opportunities."

### Step 5.4 — Alerts Page (*parallel with 5.1*)
- Active alerts list with toggles
- Create alert form: keyword, category, score threshold, region, cadence selector
- Triggered opportunities section
- Empty state: "No alerts match your current filters."

### Step 5.5 — Settings Page (*parallel with 5.1*)
- Sections: Profile, Plan/Subscription, Notifications, Data Preferences, API Access (placeholder)
- Clean, functional, minimal

### Step 5.6 — Landing Page (*parallel with 5.1*)
- Hero: headline "Find product ideas people are already searching for" + subheadline + CTA "Explore Ideas" + secondary "View Demo"
- Subtle abstract background glow + dashboard preview mockup
- Social proof strip
- Feature highlights (3–4 blocks)
- How it works section
- Sample opportunity cards (real data)
- Final CTA section
- Premium, high-trust feel — not generic

### Step 5.7 — Auth Pages (*parallel with 5.1*)
- Login / Signup / Forgot password
- Consistent dark-first styling

**Verification:**
- Dashboard loads and displays real scored ideas from API
- Filters narrow results instantly
- Idea detail page shows full score breakdown with chart
- Save/unsave works and persists
- Alerts CRUD works end-to-end
- Export generates downloadable file
- Landing page renders at pixel-perfect fidelity to UI/UX prompt
- All empty states render correctly
- Keyboard navigation works throughout
- Contrast meets accessibility standards

---

## Phase 6: Polish, Observability & Launch Prep

### Step 6.1 — Analytics Integration
- PostHog/Mixpanel events: signup, idea viewed, idea saved, note added, export started/completed, alert created, filter used, search used
- Sentry for error monitoring (frontend + backend)

### Step 6.2 — Performance Optimization
- Redis caching for hot API responses (ideas list, popular clusters)
- Next.js ISR/SSR strategy for landing page
- Image/asset optimization
- API response pagination verified under load

### Step 6.3 — Operational Monitoring (*parallel with 6.2*)
- Prometheus + Grafana for infra metrics (ingestion success rate, job duration, source freshness, API latency, error rate)
- Uptime monitoring for public endpoints
- Source freshness labels visible in admin

### Step 6.4 — Security Hardening
- Input validation on all endpoints (Pydantic)
- Rate limiting on public endpoints
- Secrets in env vars / secret manager
- Audit logging (audit_logs table) for admin actions
- No sensitive data in logs
- CORS configuration

### Step 6.5 — Responsive & Accessibility Pass
- Responsive across desktop and tablet
- Keyboard navigability
- Focus states on all interactive elements
- Contrast validation (WCAG AA minimum)
- Descriptive labels on all controls

### Step 6.6 — Final QA & Launch
- End-to-end testing of primary user journey (open dashboard → search/filter → scan cards → open detail → review evidence → save → set alert)
- Cross-browser testing
- Production deployment: frontend on Vercel, backend on chosen host, DB on managed PostgreSQL
- DNS, SSL, environment config
- Soft launch / waitlist activation

**Verification:**
- Analytics events fire correctly in PostHog/Mixpanel
- Sentry captures errors
- Page load times acceptable
- All security checks pass
- Accessibility audit passes
- Full user journey works in production

---

## Relevant Files (to create)

### Frontend (`/frontend`)
- `tailwind.config.ts` — brand color tokens, typography, spacing scale
- `app/layout.tsx` — app shell with sidebar + top bar
- `app/page.tsx` — landing page
- `app/dashboard/page.tsx` — main dashboard
- `app/ideas/[id]/page.tsx` — idea detail
- `app/saved/page.tsx` — saved ideas workspace
- `app/alerts/page.tsx` — alerts management
- `app/settings/page.tsx` — settings
- `components/ui/` — shadcn/ui primitives + custom components (IdeaCard, ScoreBadge, FilterChips, TrendIndicator, Sidebar, TopBar)
- `lib/api.ts` — API client for backend communication

### Backend (`/backend`)
- `app/main.py` — FastAPI app entry
- `app/routers/auth.py` — auth endpoints
- `app/routers/ideas.py` — ideas CRUD + search
- `app/routers/clusters.py` — cluster endpoints
- `app/routers/saved_ideas.py` — saved ideas CRUD
- `app/routers/alerts.py` — alerts CRUD
- `app/routers/exports.py` — export generation
- `app/routers/admin.py` — admin controls
- `app/models/` — SQLAlchemy models for all entities
- `app/schemas/` — Pydantic request/response schemas
- `app/services/scoring.py` — opportunity scoring engine
- `app/services/clustering.py` — semantic clustering
- `app/services/ingestion/` — source connectors (Google Trends, Autocomplete)
- `app/services/normalization.py` — cleaning pipeline
- `app/services/pipeline.py` — orchestration of full pipeline
- `app/workers/` — Celery/RQ task definitions
- `alembic/` — database migrations

---

## Decisions
- **Modular monolith** for MVP backend — simpler to ship, debug, and iterate; evolve to services later
- **Dark mode only** — brand identity is dark-first; no light mode for MVP
- **PostgreSQL full-text search** for MVP — upgrade to OpenSearch/Elasticsearch only if needed at scale
- **Google Trends + Autocomplete** as initial data sources — expand to Reddit, YouTube, marketplace signals post-MVP
- **Deterministic scoring** first — add ML refinement only if needed later
- **Auth.js / Clerk** for auth — fastest path to secure authentication
- **Hybrid clustering** (semantic embeddings + rules) — balance quality vs complexity for MVP

## Scope Boundaries
- **Included:** Full pipeline (ingestion → scoring), dashboard, detail, saved ideas, alerts, export, landing page, auth, admin controls
- **Excluded from MVP:** Predictive demand signals, team workspaces, API access for third parties, real-time streaming, full market sizing, light mode, mobile-native app

---

## Further Considerations
1. **Embedding model choice** — OpenAI embeddings vs open-source sentence-transformers? Recommendation: start with sentence-transformers (all-MiniLM-L6-v2) to avoid API cost/dependency; switch to OpenAI if quality insufficient.
2. **Pricing/subscription infrastructure** — Stripe integration not detailed in PRD. Recommendation: add Stripe billing in Phase 6 or as a fast-follow after MVP launch.
3. **Data source legal compliance** — Google Trends/Autocomplete scraping has ToS implications. Recommendation: use official APIs where available; document compliance approach before launch.
