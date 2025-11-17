from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, Hashable, Tuple, TypeVar

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: float


class TTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        self._store: Dict[Hashable, CacheEntry[Any]] = {}

    def _is_expired(self, key: Hashable) -> bool:
        entry = self._store.get(key)
        if entry is None:
            return True
        if entry.expires_at < time.time():
            self._store.pop(key, None)
            return True
        return False

    def get(self, key: Hashable) -> Any | None:
        if self._is_expired(key):
            return None
        return self._store[key].value

    def set(self, key: Hashable, value: Any) -> None:
        self._store[key] = CacheEntry(value=value, expires_at=time.time() + self._ttl)

    def cached(self, func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            key: Tuple[Hashable, ...] = (func.__name__,) + args + tuple(sorted(kwargs.items()))
            cached_value = self.get(key)
            if cached_value is not None:
                return cached_value
            value = func(*args, **kwargs)
            self.set(key, value)
            return value

        return wrapper


