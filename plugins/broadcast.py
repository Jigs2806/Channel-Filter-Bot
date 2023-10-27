import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# Import your custom modules here (info.py, utils.py, and script.py)

# Define your admin user(s)
ADMIN = [123456789]  # Replace with your admin user(s)

# Create a Pyrogram client
app = Client("my_bot")

# Create a command handler for broadcasting
@app.on_message(filters.command('broadcast') & filters.user(ADMIN))
async def broadcast_command_handler(bot, message):
    if not message.reply_to_message:
        return await message.reply("Use this command as a reply to any message!")

    m = await message.reply("Broadcasting...")

    count, users = await get_users()
    stats = "⚡ Broadcast Processing.."
    br_msg = message.reply_to_message
    total = count
    remaining = total
    success = 0
    failed = 0

    for user in users:
        chat_id = user["_id"]
        trying = await copy_msgs(br_msg, chat_id)
        if not trying:
            failed += 1
            remaining -= 1
        else:
            success += 1
            remaining -= 1
        try:
            await m.edit(script.BROADCAST.format(stats, total, remaining, success, failed))
        except Exception as e:
            print(f"Failed to edit message: {e}")
    
    stats = "✅ Broadcast Completed"
    await m.reply(script.BROADCAST.format(stats, total, remaining, success, failed))
    await m.delete()

async def copy_msgs(br_msg, chat_id):
    try:
        await br_msg.copy(chat_id)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        await copy_msgs(br_msg, chat_id)
    except Exception as e:
        print(f"Failed to copy message: {e}")
        return False

if __name__ == "__main__":
    app.run()
        
