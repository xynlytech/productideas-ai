Here are the answers based on what's actually in your codebase:

1. Where is the DB / Backend / Deploy?
Component	Current Setup	Recommendation for Production
Database	Already pointing to Supabase (PostgreSQL on aws-1-ap-northeast-2.pooler.supabase.com)	Keep Supabase — it's already wired up. Free tier handles MVP traffic fine.
Redis	Local Docker container	Upstash Redis (serverless, free tier = 10K commands/day) or Railway Redis
Backend	Local Docker / Uvicorn	Railway or Render — both deploy from Dockerfile with zero config. Railway is simpler.
Frontend	Local Docker / Next.js	Vercel — native Next.js support, free tier is generous. Just connect your repo.
Object Storage (exports)	Local MinIO	Supabase Storage (you already have the project) or keep S3-compatible with Cloudflare R2 (free egress)
Celery Worker	Not deployed yet	Same host as backend (Railway lets you run multiple services from one repo)
TL;DR: Supabase (DB + Storage) + Vercel (frontend) + Railway (backend + worker + Redis). All have free tiers.

2. What External APIs Do You Need?
API	Purpose	Required?	Cost
Google Trends	Fetches trending topics — already implemented, no API key needed (scrapes public endpoint)	✅ Built-in	Free
Google Autocomplete	Fetches search suggestions — already implemented, no API key needed (public endpoint)	✅ Built-in	Free
Sentry	Error monitoring	Optional but recommended	Free tier (5K errors/mo)
PostHog	Product analytics	Optional but recommended	Free tier (1M events/mo)
That's it. The data ingestion pipeline uses public Google endpoints — no paid API keys required for the core product to work. The GOOGLE_TRENDS_API_KEY in config exists as a placeholder but the connectors don't actually use it.

3. What Inputs Do I Need From You?
To deploy, I need these decisions/values:

#	What	Why
1	Your domain name (if any)	To configure CORS and frontend env vars
2	Supabase project password	Already in docker-compose — do you want to rotate it before going live? ⚠️ The current password is exposed in docker-compose.yml:55-56
3	Deployment platform choice	Railway/Render for backend, Vercel for frontend — or something else?
4	Sentry DSN (optional)	Create free project at sentry.io → get DSN string
5	PostHog API key (optional)	Create free project at posthog.com → get key
6	Seed search queries	What product categories/niches should the pipeline monitor? (e.g., "SaaS tools", "health supplements", "AI apps") — these feed into the ingestion connectors
Security note: Your Supabase credentials and SECRET_KEY are hardcoded in docker-compose.yml:55-62. Before deploying, these should be moved to environment variables/secrets on your hosting platform and the values rotated.