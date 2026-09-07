import asyncio
from db import create_db_and_tables

asyncio.run(create_db_and_tables())
print("Tables created successfully")