# Design

## Setting

`ADMIN_RATE_LIMIT_PER_MINUTE` controls the limit.

## Limiter

The limiter stores counters in process memory by endpoint, client host, and minute window.

This is suitable for single-instance private staging. Production multi-instance deployments should replace it with Redis, reverse-proxy, or provider-level rate limiting.
