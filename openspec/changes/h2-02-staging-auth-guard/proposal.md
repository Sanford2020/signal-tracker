# H2-02 Staging Auth Guard

The app can now be deployed to a public staging URL. The remaining risk is that bootstrap/admin-style endpoints still rely on local-development assumptions.

This change adds a small staging-safe guard: production mode requires `ADMIN_API_KEY`, and `/auth/bootstrap` requires callers to provide it through `X-Admin-Secret`.
