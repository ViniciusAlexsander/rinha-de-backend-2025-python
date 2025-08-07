import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL =", DATABASE_URL)

async def get_db_pool():
    retries = 10
    for i in range(retries):
        try:
            return await asyncpg.create_pool(DATABASE_URL)
        except Exception as e:
            print(f"Attempt {i + 1} failed: {e}")
            await asyncio.sleep(2)
    raise Exception("Could not connect to the database after several attempts")
