# Design

`GET /api/v1/health` remains a lightweight process check.

`GET /api/v1/ready` executes `SELECT 1` through the configured database session. It returns `200` when ready and `503` when the database probe fails.
