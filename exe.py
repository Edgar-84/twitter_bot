import asyncio
from bot.exe_bots import exe_bot
from db.create_tables import create_tables


async def main():
    await create_tables()
    await exe_bot()


if __name__ == "__main__":
    asyncio.run(main())
