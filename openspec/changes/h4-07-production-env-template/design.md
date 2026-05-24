# Design

`.env.production.example` lists all staging/production keys with explicit placeholders.

`check-env-readiness.ps1` rejects values containing `<placeholder>` or `CHANGE_ME`, so the template cannot accidentally pass as a real deployment env file.
