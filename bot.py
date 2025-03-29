import os
import datetime
import logging
import asyncio
import sqlite3
import asqlite
import twitchio
from twitchio import eventsub
from twitchio.ext import commands, routines
 
LOGGER: logging.Logger = logging.getLogger("Bot")

# formatting like this should make each command on a separate line
help_msg = '''
thechosenbot (1.0) by sethechosenone_________________________________ Here's a list of available commands (with more to come!):________________________________________ !help - display this help message________________ !insta - link to sethechosenone on Instagram__ !tiktok - link to sethechosenone on TikTok_____ !youtube - link to sethechosenone on YouTube
'''
follow_reminder_msg = '''Sup nerds, if you're enjoying the stream, don't forget to follow, so you can be notified everytime sethechosenone goes live!
Alternatively, if you're REALLY enjoying the stream, leaving a donation would be greatly appreciated! -> https://streamlabs.com/sethechosenone/tip'''

class Bot(commands.Bot):
    def __init__(self, *, token_database) -> None:
        self.token_database = token_database
        super().__init__(
            client_id = os.environ['CLIENT_ID'],
            client_secret = os.environ['CLIENT_SECRET'],
            bot_id = os.environ['BOT_ID'],
            owner_id = os.environ['OWNER_ID'],
            prefix = os.environ['BOT_PREFIX']
        )

    async def setup_hook(self) -> None:
        await self.add_component(SocialsComponent(self))
        subscription = eventsub.ChatMessageSubscription(
            broadcaster_user_id = os.environ['OWNER_ID'],
            user_id = os.environ['BOT_ID']
        )
        await self.subscribe_websocket(payload = subscription)

    async def add_token(self, token: str, refresh: str) -> twitchio.authentication.ValidateTokenPayload:
        response: twitchio.authentication.ValidateTokenPayload = await super().add_token(token, refresh)
        query = f'''
        INSERT INTO tokens (user_id, token, refresh) VALUES (?, ?, ?)
        ON CONFLICT (user_id) DO
        UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        '''
        async with self.token_database.acquire() as connection:
            await connection.execute(query, (response.user_id, token, refresh))
        LOGGER.info("Added token to DB for user %s", response.user_id)
        return response
    
    async def load_tokens(self, path: str | None = None):
        async with self.token_database.acquire() as connection:
            rows: list[sqlite3.Row] = await connection.fetchall('''SELECT * FROM tokens''')
        for row in rows:
            await self.add_token(row["token"], row["refresh"])
    
    async def setup_database(self) -> None:
        query = '''
        CREATE TABLE IF NOT EXISTS tokens (
            user_id TEXT PRIMARY KEY,
            token TEXT NOT NULL,
            refresh TEXT NOT NULL
        );
        '''
        async with self.token_database.acquire() as connection:
            await connection.execute(query)

    @routines.routine(delta = datetime.timedelta(minutes = 10))
    async def follow_reminder(self):
        LOGGER.info("Running routine: follow_reminder")
        user = self.create_partialuser(user_id = self.owner_id)
        await user.send_message(sender = self.bot_id, message = follow_reminder_msg)

    async def event_ready(self):
        LOGGER.info("thechosenbot is ready.")
        self.follow_reminder.start()

class SocialsComponent(commands.Component):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(name = 'help')
    async def help(self, ctx: commands.Context):
        await ctx.send(help_msg)

    @commands.command(name = 'insta')
    async def insta(self, ctx: commands.Context):
        await ctx.send('You can follow sethechosenone on Instagram here: https://www.instagram.com/sethechosenone/')

    @commands.command(name = 'tiktok')
    async def tiktok(self, ctx: commands.Context):
        await ctx.send('You can follow sethechosenone on TikTok here: https://www.tiktok.com/@sethechosenone')

    @commands.command(name = 'youtube')
    async def youtube(self, ctx: commands.Context):
        await ctx.send('You can subscribe to sethechosenone on YouTube here: https://www.youtube.com/@sethechosenone')

if __name__ == "__main__":
    twitchio.utils.setup_logging(level=logging.INFO)
    async def runner() -> None:
        async with asqlite.create_pool("tokens.db") as tdb, Bot(token_database = tdb) as bot:
            await bot.setup_database()
            await bot.start()
    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Ctrl+C received, exiting...goodbye!")