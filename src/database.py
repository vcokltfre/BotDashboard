from os import getenv
from datetime import datetime, timedelta

from asyncpg import create_pool, Record


class Database:
    """A database interface for the API to connect to Postgres."""

    async def setup(self):
        self.pool = await create_pool(
            host=getenv("DB_HOST", "127.0.0.1"),
            port=getenv("DB_PORT", 5432),
            database=getenv("DB_DATABASE"),
            user=getenv("DB_USER", "root"),
            password=getenv("DB_PASS", "password"),
        )

        with open("./data/init.sql") as f:
            await self.execute(f.read())

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def get_session(self, id: str) -> Record:
        return await self.fetch("SELECT * FROM DiscordSessions WHERE id = $1 AND valid_until < $2;", id, datetime.utcnow())

    async def get_session_member_id(self, id: int) -> Record:
        return await self.fetch("SELECT * FROM DiscordSessions WHERE member_id = $1 AND valid_until < $2;", id, datetime.utcnow())

    async def create_session(self, id: str, member_id: int, expire: int = 3600) -> Record:
        await self.execute("DELETE FROM DiscordSessions WHERE member_id = $1;", member_id)
        await self.execute("INSERT INTO DiscordSessions VALUES ($1, $2, $3);", id, member_id, (datetime.utcnow() + timedelta(seconds=expire)))
