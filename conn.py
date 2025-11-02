import aiomysql
from contextlib import asynccontextmanager

pool = None
async def connect_db():
    global pool
    if pool is None:
        pool = await aiomysql.create_pool(           
            host='localhost', 
            port=3306,           
            user='root',         
            password='agchristie02!',       
            db='berrybot',
            autocommit=True,
            minsize=1,
            maxsize=5
        )
    
    return pool

@asynccontextmanager
async def get_cursor():
    pool = await connect_db()
    async with pool.acquire() as conn:
        async with conn.cursor() as cursor:
            yield cursor