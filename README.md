# ProductIdeas AI

Premium demand intelligence SaaS that discovers product opportunities from search signals.

## Architecture

- **Frontend:** Next.js 14 (App Router) + TypeScript + Tailwind CSS + shadcn/ui
- **Backend:** Python FastAPI + SQLAlchemy + Alembic
- **Database:** PostgreSQL + Redis
- **Pipeline:** Google Trends + Autocomplete → Normalization → Clustering → Scoring

## Quick Start

```bash
# Start all services
docker-compose up -d

# Backend only
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload

# Frontend only
cd frontend && npm install && npm run dev
```

## Project Structure

```
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── core/     # Config, database, security
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── routers/  # API endpoints
│   │   ├── services/ # Business logic (scoring, clustering, ingestion)
│   │   └── workers/  # Background tasks
│   ├── alembic/      # Database migrations
│   └── tests/
├── frontend/         # Next.js frontend
│   ├── app/          # App Router pages
│   ├── components/   # Reusable components
│   └── lib/          # Utilities, API client
└── docker-compose.yml
```
