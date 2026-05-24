import os
import asyncpg
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://botuser:botpassword@db:5432/hayit_bot")

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id     BIGINT PRIMARY KEY,
                first_name  TEXT,
                username    TEXT,
                joined_at   TIMESTAMP DEFAULT NOW(),
                is_active   BOOLEAN DEFAULT TRUE
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id          SERIAL PRIMARY KEY,
                user_id     BIGINT REFERENCES users(user_id),
                name        TEXT,
                holiday     TEXT,
                created_at  TIMESTAMP DEFAULT NOW()
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                id           SERIAL PRIMARY KEY,
                name         TEXT,
                holiday      TEXT,
                theme_index  INTEGER,
                file_id      TEXT,
                created_at   TIMESTAMP DEFAULT NOW(),
                UNIQUE (name, holiday, theme_index)
            );
        """)
    logger.info("DB jadvallar tayyor ✅")


# ─── USERS ────────────────────────────────────────────────────────────────────

async def save_user(user_id: int, first_name: str, username: str = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, first_name, username)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE
                SET first_name = EXCLUDED.first_name,
                    username   = EXCLUDED.username,
                    is_active  = TRUE;
        """, user_id, first_name, username)


async def get_all_active_users() -> list[int]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users WHERE is_active = TRUE;")
        return [r["user_id"] for r in rows]


async def deactivate_user(user_id: int):
    """Foydalanuvchi botni block qilsa, is_active = FALSE qilamiz"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_active = FALSE WHERE user_id = $1;", user_id
        )


# ─── REQUESTS ─────────────────────────────────────────────────────────────────

async def save_request(user_id: int, name: str, holiday: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, first_name, username)
            VALUES ($1, 'unknown', null)
            ON CONFLICT (user_id) DO NOTHING;
        """, user_id)
        await conn.execute("""
            INSERT INTO requests (user_id, name, holiday)
            VALUES ($1, $2, $3);
        """, user_id, name, holiday)


async def get_stats() -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        total_users    = await conn.fetchval("SELECT COUNT(*) FROM users;")
        total_requests = await conn.fetchval("SELECT COUNT(*) FROM requests;")
        today_requests = await conn.fetchval(
            "SELECT COUNT(*) FROM requests WHERE created_at::date = CURRENT_DATE;"
        )
        popular_names  = await conn.fetch("""
            SELECT name, COUNT(*) as cnt
            FROM requests
            GROUP BY name
            ORDER BY cnt DESC
            LIMIT 5;
        """)
        by_holiday = await conn.fetch("""
            SELECT holiday, COUNT(*) as cnt
            FROM requests
            GROUP BY holiday
            ORDER BY cnt DESC;
        """)
    return {
        "total_users":    total_users,
        "total_requests": total_requests,
        "today_requests": today_requests,
        "popular_names":  [(r["name"], r["cnt"]) for r in popular_names],
        "by_holiday":     [(r["holiday"], r["cnt"]) for r in by_holiday],
    }


# ─── CACHE ────────────────────────────────────────────────────────────────────

async def get_cached_file_id(name: str, holiday: str, theme_index: int) -> str | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT file_id FROM cache
            WHERE name = $1 AND holiday = $2 AND theme_index = $3;
        """, name, holiday, theme_index)
        return row["file_id"] if row else None


async def save_cache(name: str, holiday: str, theme_index: int, file_id: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO cache (name, holiday, theme_index, file_id)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (name, holiday, theme_index) DO UPDATE
                SET file_id = EXCLUDED.file_id;
        """, name, holiday, theme_index, file_id)
