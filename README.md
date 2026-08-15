# WhatsApp AI Assistant

Production-grade WhatsApp AI conversation assistant with reliability-first architecture.

## Architecture

```text
WhatsApp -> Webhook -> FastAPI -> Redis Queue -> Worker -> LLM -> Validation -> Mock WhatsApp
```

## Prerequisites

- Docker + Docker Compose
- Python 3.12
- Node.js 20
- Gemini API key (optional; mock mode works without it)

## Quick Start

```bash
cd whatsapp-ai-assistant
cp .env.example .env
docker compose up
```

Services:
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

## Environment Variables

See `.env.example`. Key variables:

- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `GEMINI_API_KEY` — Google Gemini API key
- `WHATSAPP_ACCESS_TOKEN` — WhatsApp Business API token
- `WHATSAPP_PHONE_NUMBER_ID` — WhatsApp phone number ID
- `WHATSAPP_VERIFY_TOKEN` — Webhook verification token

## Testing

```bash
cd apps/api
python -m pytest tests/ -v
```

## Notes

- Real WhatsApp sending is disabled by default. Mock providers are enabled when credentials are missing.
- The first milestone is a complete mock pipeline: webhook -> PostgreSQL -> Redis queue -> mock Gemini -> approval queue -> dashboard.

## Project Structure

```text
whatsapp-ai-assistant/
├── apps/
│   ├── web/                 # Next.js dashboard
│   └── api/                 # FastAPI backend
│       ├── app/
│       │   ├── api/         # Route definitions
│       │   ├── core/        # Config, DB, Redis
│       │   ├── models/      # SQLAlchemy models
│       │   ├── schemas/     # Pydantic schemas
│       │   ├── providers/   # LLM + Messaging abstractions
│       │   ├── repositories/# Data access
│       │   ├── services/    # Business logic
│       │   └── workers/     # Queue consumer
│       └── tests/           # Backend tests
├── infra/
│   ├── docker/              # Dockerfiles
│   └── docker-compose.yml
├── packages/
│   ├── shared-types/
│   └── config/
├── scripts/
├── docs/
├── .env.example
├── README.md
└── LICENSE
```
