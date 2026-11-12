"""Database settings and engine.

The connection URL comes from the environment (``BIO_DATABASE_URL``, see .env.example), so no
credentials live in the code. The engine is created on first use.
"""

import os
from functools import lru_cache

from sqlalchemy import Engine, create_engine


@lru_cache
def get_engine() -> Engine:
    url = os.environ.get("BIO_DATABASE_URL")
    if not url:
        raise RuntimeError("BIO_DATABASE_URL is not set (see .env.example)")
    return create_engine(url, pool_pre_ping=True, pool_recycle=1800)
