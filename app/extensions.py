import json
import logging
from typing import Any

from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

try:
    import redis
except Exception:  # pragma: no cover
    redis = None


db = SQLAlchemy()
migrate = Migrate()
cors = CORS()


class CacheStore:
    def __init__(self) -> None:
        self.client = None
        self.memory_store: dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)

    def init_app(self, app) -> None:
        if redis is None:
            self.logger.warning("Redis package unavailable, using in-memory cache.")
            return

        try:
            self.client = redis.Redis.from_url(app.config["REDIS_URL"], decode_responses=True)
            self.client.ping()
        except Exception as exc:  # pragma: no cover
            self.logger.warning("Redis unavailable, using in-memory cache: %s", exc)
            self.client = None

    def get_json(self, key: str) -> Any:
        if self.client:
            raw_value = self.client.get(key)
            return json.loads(raw_value) if raw_value else None
        return self.memory_store.get(key)

    def set_json(self, key: str, value: Any, ex: int = 3600) -> None:
        if self.client:
            self.client.setex(key, ex, json.dumps(value, ensure_ascii=False))
            return
        self.memory_store[key] = value

    def delete(self, key: str) -> None:
        if self.client:
            self.client.delete(key)
            return
        self.memory_store.pop(key, None)


cache = CacheStore()


def init_extensions(app) -> None:
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    cache.init_app(app)

