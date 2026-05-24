# H4-05 Admin Rate Limit

The bootstrap endpoint is protected by `ADMIN_API_KEY`, but public staging should also throttle repeated attempts.

This change adds a simple in-memory fixed-window limiter for admin endpoints.
