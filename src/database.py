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

        self.owners = [int(u) for u in getenv("STAFF", "").split(";") if u]

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
        return await self.fetchrow("SELECT * FROM DiscordSessions WHERE id = $1 AND valid_until > $2;", id, datetime.utcnow())

    async def get_session_member_id(self, id: int) -> Record:
        return await self.fetchrow("SELECT * FROM DiscordSessions WHERE member_id = $1 AND valid_until > $2;", id, datetime.utcnow())

    async def create_session(self, id: str, member_id: int, expire: int = 3600) -> Record:
        await self.execute("DELETE FROM DiscordSessions WHERE member_id = $1;", member_id)
        await self.execute("INSERT INTO DiscordSessions VALUES ($1, $2, $3);", id, member_id, (datetime.utcnow() + timedelta(seconds=expire)))

    async def get_access(self, bot: int, guild: int, member: int) -> bool:
        return member in self.owners or bool(await self.fetchrow(
            "SELECT * FROM ConfigAccess WHERE bot_id = $1 AND guild_id = $2 AND member_id = $3;",
            bot, guild, member,
        ))

    async def get_bot(self, bot: int) -> Record:
        return await self.fetchrow("SELECT * FROM Bots WHERE bot_id = $1;", bot)

    async def get_config(self, guild: int, bot: int) -> Record:
        return await self.fetchrow("SELECT * FROM Configs WHERE guild_id = $1 AND bot_id = $2;", guild, bot)

    async def set_config(self, guild: int, bot: int, data: str) -> None:
        await self.execute("UPDATE Configs SET config = $1 WHERE guild_ID = $2 AND bot_id = $3;", data, guild, bot)

    async def api_create_bot(self, botid: int, botname: str) -> None:
        await self.execute("INSERT INTO Bots VALUES ($1, $2);", botid, botname)

    async def api_delete_bot(self, botid: int) -> None:
        await self.execute("DELETE FROM Bots WHERE bot_id = $1;", botid)

    async def api_create_config(self, guildid: int, botid: int, guildname: str, data: str) -> None:
        await self.execute("INSERT INTO Configs VALUES ($1, $2, $3, $4);", guildid, guildname, botid, data)

    async def api_delete_config(self, guildid: int, botid: int) -> None:
        await self.execute("DELETE FROM Configs WHERE guild_id = $1 AND bot_id = $2;", guildid, botid)

    async def api_add_user(self, guildid: int, botid: int, member_id: int) -> None:
        await self.execute("INSERT INTO ConfigAccess VALUES ($1, $2, $3);", guildid, botid, member_id)

    async def api_delete_user(self, guildid: int, botid: int, member_id: int) -> None:
        await self.execute("DELETE FROM ConfigAccess WHERE guild_id = $1 AND bot_id = $2 AND member_id = $3;", guildid, botid, member_id)
