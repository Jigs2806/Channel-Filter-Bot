from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from time import time
from client import User
from utils import (
    force_sub,
    get_group_info,
    update_group_info,
    search_imdb,
    save_dlt_message
)

# Define your admin user(s)
ADMIN = [123456789]  # Replace with your admin user(s)

# Create a Pyrogram client
app = Client("my_bot")

# Define message handlers
@app.on_message(filters.text & filters.group & filters.incoming & ~filters.command(["verify", "connect", "id"]))
async def search_command_handler(client, message):
    f_sub = await force_sub(client, message)

    if f_sub is False:
        return

    group_info = await get_group_info(message.chat.id)
    channels = group_info.get("channels", [])

    if not channels:
        return

    if message.text.startswith("/"):
        return

    query = message.text
    head = "<u>Here are the results 👇\n\nPromoted By </u> <b><i>@Cineheart_Movies</i></b>\n\n"
    results = ""

    try:
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = (msg.text or msg.caption).split("\n")[0]

                if name in results:
                    continue

                results += f"<b><i>🍿 {name}\n🔗 {msg.link}</i></b>\n\n"

        if not results:
            movies = await search_imdb(query)
            buttons = []

            for movie in movies:
                buttons.append([InlineKeyboardButton(movie['title'], callback_data=f"recheck_{movie['id']}")])

            msg = await message.reply_photo(
                photo="https://telegra.ph/file/f9a424f114b9725f79dfb.jpg",
                caption="<b><i>I couldn't find anything related to your query 😕. Did you mean any of these?</i></b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        else:
            msg = await message.reply_text(text=head + results, disable_web_page_preview=True)

        _time = int(time()) + (15 * 900)
        await save_dlt_message(msg, _time)

    except Exception as e:
        print(f"Error in search_command_handler: {e}")

@app.on_callback_query(filters.regex(r"^recheck"))
async def recheck_command_handler(client, update):
    clicked = update.from_user.id

    try:
        typed = update.message.reply_to_message.from_user.id
    except:
        return await update.message.delete(2)

    if clicked != typed:
        return await update.answer("That's not for you! 👀", show_alert=True)

    m = await update.message.edit("Searching..💥")
    id = update.data.split("_")[-1]
    query = await search_imdb(id)
    group_info = await get_group_info(update.message.chat.id)
    channels = group_info.get("channels", [])
    head = "<u>I Have Searched Movie With Wrong Spelling But Take care next time 👇\n\nPromoted By </u> <b><i>@Cineheart_Movies</i></b>\n\n"
    results = ""

    try:
        for channel in channels:
            async for msg in User.search_messages(chat_id=channel, query=query):
                name = (msg.text or msg.caption).split("\n")[0]

                if name in results:
                    continue

                results += f"<b><i>❤️‍🔥🍿 {name}</i></b>\n\n🔗 {msg.link}</i></b>\n\n"

        if not results:
            return await update.message.edit("Still no results found! Please Request To Group Admin", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Request To Admin 🎯", callback_data=f"request_{id}")]]))

        await update.message.edit(text=head + results, disable_web_page_preview=True)

    except Exception as e:
        print(f"Error in recheck_command_handler: {e}")

@app.on_callback_query(filters.regex(r"^request"))
async def request_command_handler(client, update):
    clicked = update.from_user.id

    try:
        typed = update.message.reply_to_message.from_user.id
    except:
        return await update.message.delete()

    if clicked != typed:
        return await update.answer("That's not for you! 👀", show_alert=True)

    group_info = await get_group_info(update.message.chat.id)
    admin = group_info.get("user_id")
    id = update.data.split("_")[1]
    name = await search_imdb(id)
    url = f"https://www.imdb.com/title/tt{id}"
    text = f"#RequestFromYourGroup\n\nName: {name}\nIMDb: {url}"
    await client.send_message(chat_id=admin, text=text, disable_web_page_preview=True)
    await update.answer("✅ Request Sent To Admin", show_alert=True)
    await update.message.delete(60)

if __name__ == "__main__":
    app.run()
    
