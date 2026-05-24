# H4-07 Production Env Template

Operators need a production-like env template separate from the local development `.env.example`.

This change adds `.env.production.example` and makes readiness checks reject placeholder values.
