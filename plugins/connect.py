from pyrogram import Client, filters
from pyrogram.types import Message
from info import *
from utils import *

# Define your admin user(s)
ADMIN = [123456789]  # Replace with your admin user(s)

# Create a Pyrogram client
app = Client("my_bot")

# Define message handlers
@app.on_message(filters.group & filters.command("connect"))
async def connect_command_handler(client, message: Message):
    m = await message.reply("Connecting...")

    # Get information about the group
    group_info = await get_group_info(message.chat.id)
    
    if not group_info:
        return await bot.leave_chat(message.chat.id)
    
    user_id = group_info.get("user_id")
    user_name = group_info.get("user_name")
    verified = group_info.get("verified")
    channels = group_info.get("channels", [])

    if message.from_user.id != user_id:
        return await m.edit(f"Only {user_name} can use this command 😁")
    
    if not verified:
        return await m.edit("This chat is not verified! Use /verify")
    
    try:
        channel_id = int(message.command[-1])
        if channel_id in channels:
            return await message.reply("This channel is already connected. You can't connect again.")
        
        channels.append(channel_id)
    except (ValueError, IndexError):
        return await m.edit("❌ Incorrect format! Use `/connect ChannelID`")
    
    try:
        chat = await client.get_chat(channel_id)
        c_link = chat.invite_link
        await client.join_chat(c_link)
    except Exception as e:
        if "The user is already a participant" in str(e):
            pass
        else:
            text = f"❌ Error: `{str(e)}`\nMake sure I'm an admin in that channel, this group has all necessary permissions, and {user_name} is not banned there."
            return await m.edit(text)
    
    await update_group_info(message.chat.id, {"channels": channels})
    await m.edit(f"✅ Successfully connected to [{chat.title}]({c_link})!", disable_web_page_preview=True)

@app.on_message(filters.group & filters.command("disconnect"))
async def disconnect_command_handler(client, message: Message):
    m = await message.reply("Please wait...")

    # Get information about the group
    group_info = await get_group_info(message.chat.id)
    
    if not group_info:
        return await bot.leave_chat(message.chat.id)
    
    user_id = group_info.get("user_id")
    user_name = group_info.get("user_name")
    verified = group_info.get("verified")
    channels = group_info.get("channels", [])

    if message.from_user.id != user_id:
        return await m.edit(f"Only {user_name} can use this command 😁")
    
    if not verified:
        return await m.edit("This chat is not verified! Use /verify")
    
    try:
        channel_id = int(message.command[-1])
        if channel_id not in channels:
            return await m.edit("You haven't added this channel yet or the channel ID is incorrect.")
        
        channels.remove(channel_id)
    except (ValueError, IndexError):
        return await m.edit("❌ Incorrect format! Use `/disconnect ChannelID`")
    
    try:
        chat = await client.get_chat(channel_id)
        c_link = chat.invite_link
        await client.leave_chat(channel_id)
    except Exception as e:
        text = f"❌ Error: `{str(e)}`\nMake sure I'm an admin in that channel, this group has all necessary permissions, and {user_name} is not banned there."
        return await m.edit(text)
    
    await update_group_info(message.chat.id, {"channels": channels})
    await m.edit(f"✅ Successfully disconnected from [{chat.title}]({c_link})!", disable_web_page_preview=True)

@app.on_message(filters.group & filters.command("connections"))
async def connections_command_handler(client, message: Message):
    group_info = await get_group_info(message.chat.id)

    if not group_info:
        return await message.reply("Group information not found. Use /connect to set up group information.")
    
    user_id = group_info.get("user_id")
    user_name = group_info.get("user_name")
    channels = group_info.get("channels", [])
    f_sub = group_info.get("f_sub")
    
    if message.from_user.id != user_id:
        return await message.reply(f"Only {user_name} can use this command 😁")
    
    if not channels:
        return await message.reply("This group is currently not connected to any channels. Connect one using /connect.")
    
    text = "This group is currently connected to:\n\n"
    for channel_id in channels:
        try:
            chat = await client.get_chat(channel_id)
            name = chat.title
            link = chat.invite_link
            text += f"🔗 Connected Channel - [{name}]({link})\n"
        except Exception as e:
            await message.reply(f"❌ Error in `{channel_id}`:\n`{e}`")
    
    if f_sub:
        try:
            f_chat = await client.get_chat(f_sub)
            f_title = f_chat.title
            f_link = f_chat.invite_link
            text += f"\nFSub: [{f_title}]({f_link})"
        except Exception as e:
            await message.reply(f"❌ Error in FSub (`{f_sub}`):\n`{e}`")
    
    await message.reply(text, disable_web_page_preview=True)

if __name__ == "__main__":
    app.run()
                                    
