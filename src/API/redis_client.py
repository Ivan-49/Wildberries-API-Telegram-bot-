import redis

from dotenv import load_dotenv
import os
import asyncio
import aioredis

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")




class RedisClient:
    def __init__(self, url=f"redis://{REDIS_HOST}:{REDIS_PORT}", decode_responses=True):
        self.redis = aioredis.from_url(url, decode_responses=decode_responses)

    async def save_token(self, user_id, jwt_token, ttl):
        await self.redis.set(f"token-{user_id}", jwt_token, expire=ttl)

    async def get_token(self, user_id):
        return await self.redis.get(f"token-{user_id}")

    async def add_to_blacklist(self, user_id, jwt_token):
        await self.redis.set(f"blacklist-{user_id}", jwt_token)

    async def check_blacklist(self, user_id):
        return await self.redis.get(f"blacklist-{user_id}")

    async def close_connection(self):
        await self.redis.close()
        await self.redis.wait_closed()

