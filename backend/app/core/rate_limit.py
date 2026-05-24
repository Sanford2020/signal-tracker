import threading
import time


_rate_limit_lock = threading.Lock()
_rate_limit_buckets: dict[tuple[str, int], int] = {}


class RateLimitExceededError(Exception):
    pass


def check_fixed_window_rate_limit(*, key: str, limit: int, window_seconds: int = 60) -> None:
    if limit <= 0:
        raise RateLimitExceededError("Rate limit exceeded.")

    window = int(time.time() // window_seconds)
    bucket_key = (key, window)
    with _rate_limit_lock:
        _rate_limit_buckets[bucket_key] = _rate_limit_buckets.get(bucket_key, 0) + 1
        if _rate_limit_buckets[bucket_key] > limit:
            raise RateLimitExceededError("Rate limit exceeded.")

        stale_windows = [existing for existing in _rate_limit_buckets if existing[1] < window]
        for stale_key in stale_windows:
            _rate_limit_buckets.pop(stale_key, None)


def clear_rate_limit_state() -> None:
    with _rate_limit_lock:
        _rate_limit_buckets.clear()
