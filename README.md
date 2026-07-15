# InsightFlow Analytics Platform

InsightFlow is a full-stack analytics platform for collecting product events, viewing dashboard metrics, running simple ML predictions, and receiving live dashboard updates.

The project is split into:

- `frontend/` - Next.js static frontend served by Nginx
- `backend/` - Django, Django REST Framework, Daphne, Channels, RQ workers
- `db` - PostgreSQL service from Docker Compose
- `redis` - Redis service for queues, cache, and Channels

## Architecture

When running with Docker Compose, the browser should use the frontend entry point:

```text
Browser -> http://localhost:3000 -> frontend Nginx -> backend:8000 -> Django
```

The frontend container serves static files with Nginx. API and WebSocket traffic are proxied by `frontend/nginx.conf`:

```text
/api/* -> http://backend:8000/api/*
/ws/*  -> http://backend:8000/ws/*
```

The backend is also published on `localhost:8000` in the current Compose file for direct debugging.

## Tech Stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS, Recharts
- Backend: Django 6, Django REST Framework, Daphne, Channels
- Database: PostgreSQL 15
- Cache/Queue: Redis 7, django-rq
- Runtime: Docker Compose
- CI: GitHub Actions

## Required Environment Files

Environment files are not committed to the repository. Create them locally before running Docker Compose.

### Root `.env`

Used by Docker Compose for the PostgreSQL service and frontend build arguments.

```env
COMPOSE_PROJECT_NAME=insightflow

POSTGRES_DB=insightflow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin

NEXT_PUBLIC_API_KEY=your_frontend_api_key
```

### `backend/.env`

Used by the backend and worker containers.

```env
API_KEY=secret_api_key
DJANGO_SETTINGS_MODULE=config.dev

DB_NAME=insightflow
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
```

Important Docker values:

- Use `DB_HOST=db`, not `localhost`
- Use `DB_PORT=5432`, not the host-mapped port `5433`
- Use `REDIS_HOST=redis`, not `localhost`

## Run With Docker

Build and start all services:

```bash
docker compose up -d --build
```

Open the frontend:

```text
http://localhost:3000
```

Check backend health directly:

```bash
curl http://localhost:8000/api/health/
```

Check backend health through Nginx:

```bash
curl http://localhost:3000/api/health/
```

View running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs backend
docker compose logs frontend
docker compose logs worker
```

Stop services and remove volumes:

```bash
docker compose down -v
```

## Ports

Current Compose mappings:

```text
frontend: http://localhost:3000 -> container port 80
backend:  http://localhost:8000 -> container port 8000
postgres: localhost:5433 -> container port 5432
redis:    localhost:6379 -> container port 6379
```

If the backend should only be reachable through Nginx, replace the backend `ports` mapping with:

```yaml
expose:
  - "8000"
```

With `expose`, other containers can still call `backend:8000`, but the host cannot call `localhost:8000`.

## API Endpoints

Base API path:

```text
/api/
```

Useful routes:

```text
GET  /api/health/
POST /api/login/
POST /api/login/refresh/
POST /api/signup/
GET  /api/dashboard/
POST /api/logout/
GET  /api/event/list/
POST /api/event/
GET  /api/event/stats/
GET  /api/event/count/
GET  /api/event/daily/
GET  /api/event/top/
GET  /api/analytics/funnel/
GET  /api/ml/training-data
GET  /api/ml/predict/
GET  /api/ml/validate/
```

Dashboard and analytics endpoints require authentication. A `401 Unauthorized` response means the request reached Django, but no valid login token or cookie was sent.

## WebSocket

Backend WebSocket route:

```text
ws://localhost:3000/ws/dashboard/
```

Nginx forwards `/ws/` traffic to the backend container.

## Local Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Frontend development server:

```text
http://localhost:3000
```

For Docker builds, the frontend uses `NEXT_PUBLIC_API_URL=/api` so browser requests go through Nginx.

## Local Backend Development

Using the local Python environment:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

Backend health check:

```text
http://localhost:8000/api/health/
```

For local backend development outside Docker, set `DB_HOST` and `REDIS_HOST` according to your local services.

## Background Worker

The worker service runs:

```bash
python manage.py rqworker events cache analytics notifications
```

It depends on Redis and the backend Django configuration.

## CI

GitHub Actions runs on pushes and pull requests to `master`.

The workflow:

1. Checks out the repository
2. Creates temporary `.env` files from GitHub Secrets
3. Builds Docker Compose services
4. Starts the stack
5. Waits for `http://localhost:8000/api/health/`
6. Prints logs on failure
7. Shuts down the stack

Required GitHub Secrets:

```text
API_KEY
DB_HOST
DB_NAME
DB_PASSWORD
DB_PORT
DB_USER
DJANGO_SETTINGS_MODULE
REDIS_HOST
REDIS_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
NEXT_PUBLIC_API_URL
NEXT_PUBLIC_API_KEY
```

For CI Docker values, use:

```text
DB_HOST=db
DB_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
DJANGO_SETTINGS_MODULE=config.dev
```

## Notes

- `NEXT_PUBLIC_*` values are exposed to browser JavaScript. Do not treat `NEXT_PUBLIC_API_KEY` as a private secret.
- Requests to `http://localhost:3000/api/...` hit Nginx first, then the backend.
- Requests to `http://localhost:8000/api/...` bypass Nginx and call Django directly.
- If Django reports model changes not reflected in migrations, run `python manage.py makemigrations` and commit the generated migration files.
