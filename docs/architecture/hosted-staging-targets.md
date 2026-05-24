# Hosted Staging Target Comparison

## Decision

Choose Render for the first hosted staging deployment.

## Why Render

Signal Tracker needs:

- FastAPI backend
- Celery background worker
- Postgres
- Redis-compatible broker/result backend
- Next.js frontend
- environment and secret management
- repeatable deployment configuration

Render maps directly to that shape with web services, background workers, Render Postgres, Render Key Value, and `render.yaml` Blueprints.

## Options

| Option | Fit | Strength | Risk |
| --- | --- | --- | --- |
| Render single platform | Best first staging fit | One Blueprint can describe API, worker, web, Postgres, and Redis-compatible storage | Next.js on Render is workable but less specialized than Vercel |
| Vercel + Render | Strong split | Vercel is excellent for Next.js; Render can host API/worker/data services | Two providers means more secrets, CORS, and deploy coordination |
| Railway single platform | Good | Strong developer experience for app + data services | Need more Railway-specific config decisions for worker/web split |
| Fly.io | Powerful | Good for Docker and distributed apps | More operational surface area for first staging |

## Selected First Path

Use Render single platform for H2-01.

After staging is stable, consider moving only the frontend to Vercel if frontend deploy experience becomes important enough to justify a second provider.

## Sources

- Render Blueprint YAML Reference: https://render.com/docs/blueprint-spec
- Render Background Workers: https://render.com/docs/background-workers
- Render Celery Worker: https://render.com/docs/deploy-celery
- Render Key Value: https://render.com/redis
- Render FastAPI: https://render.com/docs/deploy-fastapi
- Railway FastAPI guide: https://docs.railway.com/guides/fastapi
- Vercel environment variables: https://vercel.com/docs/environment-variables
