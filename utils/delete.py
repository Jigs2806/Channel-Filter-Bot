import asyncio
from .helpers import *
from .info import DATABASE_URI  # Import DATABASE_URI from info.py
from time import time
from client import DlBot

async def check_up(bot):
    _time = int(time())
    all_data = await get_all_dlt_data(_time)
    
    for data in all_data:
        try:
            await bot.delete_messages(chat_id=data["chat_id"], message_ids=data["message_id"])
        except Exception as e:
            error_info = {
                "❌ Error": str(e),
                "data": data
            }
            print(error_info)  # Log the error for debugging
    
    await delete_all_dlt_data(_time)

async def run_check_up():
    async with DlBot() as bot:
        while True:
            await check_up(bot)
            await asyncio.sleep(1800)  # Sleep for 30 minutes (1800 seconds)

if __name__ == "__main__":
    asyncio.run(run_check_up())
