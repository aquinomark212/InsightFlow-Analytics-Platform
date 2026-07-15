# Architecture

InsightFlow runs as a Docker Compose stack with a static frontend, reverse proxy, Django API, PostgreSQL, Redis, and a background worker.

## Services

```text
Browser
  -> frontend container
  -> backend container
  -> db / redis
```

### Frontend

The frontend is a Next.js static export built in `frontend/Dockerfile` and served by Nginx.

Host access:

```text
http://localhost:3000
```

Docker mapping:

```text
localhost:3000 -> frontend:80
```

Responsibilities:

- Serve static frontend files
- Proxy `/api/` requests to the backend
- Proxy `/ws/` WebSocket traffic to the backend

### Backend

The backend is a Django ASGI app served by Daphne.

Host access in the current Compose file:

```text
http://localhost:8000
```

Docker mapping:

```text
localhost:8000 -> backend:8000
```

Responsibilities:

- REST API
- Authentication
- Dashboard data
- Event ingestion
- ML prediction endpoints
- WebSocket consumers through Django Channels

### PostgreSQL

PostgreSQL stores application data.

Host access:

```text
localhost:5433
```

Container access:

```text
db:5432
```

The backend container should use:

```env
DB_HOST=db
DB_PORT=5432
```

### Redis

Redis is used for queues, caching, and Channels.

Host access:

```text
localhost:6379
```

Container access:

```text
redis:6379
```

The backend container should use:

```env
REDIS_HOST=redis
REDIS_PORT=6379
```

### Worker

The worker runs Django RQ queues:

```bash
python manage.py rqworker events cache analytics notifications
```

It uses the same backend image and `backend/.env` configuration.

## Request Flow

### Frontend Page Request

```text
Browser
  -> http://localhost:3000/
  -> frontend Nginx
  -> static files from /usr/share/nginx/html
```

### API Request Through Nginx

```text
Browser
  -> http://localhost:3000/api/health/
  -> frontend Nginx
  -> http://backend:8000/api/health/
  -> Django
```

The Nginx rule is:

```nginx
location /api/ {
    proxy_pass http://backend:8000;
}
```

Because `proxy_pass` does not include a replacement URI, the `/api/...` path is forwarded unchanged.

### Direct Backend Request

```text
Browser or curl
  -> http://localhost:8000/api/health/
  -> Django
```

This bypasses Nginx. It works only because the backend service currently uses:

```yaml
ports:
  - "8000:8000"
```

### WebSocket Request

```text
Browser
  -> ws://localhost:3000/ws/dashboard/
  -> frontend Nginx
  -> ws://backend:8000/ws/dashboard/
  -> Django Channels
```

The Nginx rule is:

```nginx
location /ws/ {
    proxy_pass http://backend:8000;

    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## Ports vs Expose

`ports` publishes a container port to the host machine.

```yaml
ports:
  - "8000:8000"
```

This allows:

```text
http://localhost:8000
```

`expose` only makes a port available to other containers on the same Docker network.

```yaml
expose:
  - "8000"
```

This allows:

```text
frontend -> backend:8000
```

but not:

```text
localhost:8000
```

For production-style routing, the backend can use `expose` and the frontend/Nginx can be the only public entry point.

## Docker Network

All services are attached to `app_network`.

Docker Compose gives each service a DNS name matching the service name:

```text
backend
db
redis
frontend
worker
```

That is why Nginx can call:

```text
http://backend:8000
```

and Django can connect to:

```text
db:5432
redis:6379
```

## Environment Boundaries

Root `.env` is read by Docker Compose for Compose-level variables:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
NEXT_PUBLIC_API_KEY
```

`backend/.env` is passed into backend and worker containers:

```text
API_KEY
DB_HOST
DB_NAME
DB_USER
DB_PASSWORD
DB_PORT
REDIS_HOST
REDIS_PORT
DJANGO_SETTINGS_MODULE
```

`NEXT_PUBLIC_*` values are compiled into browser JavaScript and are visible to users. They should not be treated as private secrets.

## Health Checks

Direct backend health check:

```bash
curl http://localhost:8000/api/health/
```

Nginx-proxied health check:

```bash
curl http://localhost:3000/api/health/
```

Both should return:

```json
{"status":"ok"}
```
