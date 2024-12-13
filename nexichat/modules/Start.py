import asyncio
import logging
import random
import time
import psutil
import config
from nexichat import _boot_
from nexichat import get_readable_time
from nexichat import nexichat, mongo
from datetime import datetime
from pymongo import MongoClient
from pyrogram.enums import ChatType
from pyrogram import Client, filters
from config import OWNER_ID, MONGO_URL, OWNER_USERNAME
from pyrogram.errors import FloodWait, ChatAdminRequired
from nexichat.database.chats import get_served_chats, add_served_chat
from nexichat.database.users import get_served_users, add_served_user
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from nexichat.modules.helpers import (
    START,
    START_BOT,
    PNG_BTN,
    HELP_BTON,
    CLOSE_BTN,
    HELP_BTN,
    HELP_BUTN,
    HELP_READ,
    HELP_START,
    SOURCE_READ,
)

GSTART = """**ʜᴇʏ ᴅᴇᴀʀ {}**\n\n**ᴛʜᴀɴᴋs ғᴏʀ sᴛᴀʀᴛ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ʟᴀɴɢᴜᴀɢᴇ ʙʏ ᴄʟɪᴄᴋ ᴏɴ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs.**\n**ᴄʟɪᴄᴋ ᴀɴᴅ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ғᴀᴠᴏᴜʀɪᴛᴇ ʟᴀɴɢᴜᴀɢᴇ ᴛᴏ sᴇᴛ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ ғᴏʀ ʙᴏᴛ ʀᴇᴘʟʏ.**\n\n**ᴛʜᴀɴᴋ ʏᴏᴜ ᴘʟᴇᴀsᴇ ᴇɴɪᴏʏ.**"""

BOT = "https://files.catbox.moe/kb3gl1.jpg"
IMG = [
    "https://graph.org/file/210751796ff48991b86a3.jpg",
    "https://graph.org/file/7b4924be4179f70abcf33.jpg",
    "https://graph.org/file/f6d8e64246bddc26b4f66.jpg",
    "https://graph.org/file/63d3ec1ca2c965d6ef210.jpg",
    "https://graph.org/file/9f12dc2a668d40875deb5.jpg",
    "https://graph.org/file/0f89cd8d55fd9bb5130e1.jpg",
    "https://graph.org/file/e5eb7673737ada9679b47.jpg",
    "https://graph.org/file/2e4dfe1fa5185c7ff1bfd.jpg",
    "https://graph.org/file/36af423228372b8899f20.jpg",
    "https://graph.org/file/c698fa9b221772c2a4f3a.jpg",
    "https://graph.org/file/61b08f41855afd9bed0ab.jpg",
    "https://graph.org/file/744b1a83aac76cb3779eb.jpg",
    "https://graph.org/file/814cd9a25dd78480d0ce1.jpg",
    "https://graph.org/file/e8b472bcfa6680f6c6a5d.jpg",
]



from nexichat import db

chatai = db.Word.WordDb
lang_db = db.ChatLangDb.LangCollection
status_db = db.ChatBotStatusDb.StatusCollection




async def bot_sys_stats():
    bot_uptime = int(time.time() - _boot_)
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    UP = f"{get_readable_time((bot_uptime))}"
    CPU = f"{cpu}%"
    RAM = f"{mem}%"
    DISK = f"{disk}%"
    return UP, CPU, RAM, DISK
    

async def set_default_status(chat_id):
    try:
        if not await status_db.find_one({"chat_id": chat_id}):
            await status_db.insert_one({"chat_id": chat_id, "status": "enabled"})
    except Exception as e:
        print(f"Error setting default status for chat {chat_id}: {e}")

from langdetect import detect
from collections import Counter
from pyrogram.types import Chat

async def set_group_language(chat: Chat):
    messages = []
    # Get the recent chat history for language detection
    async for message in nexichat.get_chat_history(chat.id, limit=50):
        if message.text and not message.from_user.is_bot:
            messages.append(message.text)

    if not messages:
        return  # If there are no valid messages, exit the function

    # Detect language for each message
    lang_counts = Counter(detect(text) for text in messages if text)
    most_common_lang, max_count = lang_counts.most_common(1)[0]
    max_lang_percentage = (max_count / len(messages)) * 100

    # If a single language is dominant, set it as chat language
    if max_lang_percentage > 50:
        await lang_db.update_one({"chat_id": chat.id}, {"$set": {"language": most_common_lang}}, upsert=True)
        await nexichat.send_message(
            chat.id, 
            f"This chat language has been set to {most_common_lang.title()} ({most_common_lang})."
        )

@nexichat.on_message(filters.new_chat_members)
async def welcomejej(client, message: Message):
    chat = message.chat
    await add_served_chat(message.chat.id)
    await set_default_status(message.chat.id)
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    try:
        for member in message.new_chat_members:
            
            if member.id == nexichat.id:
                try:
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"sᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ", callback_data="choose_lang")]])    
                    await message.reply_photo(photo=random.choice(IMG), caption=START.format(nexichat.mention or "can't mention", users, chats), reply_markup=reply_markup)
                    chat = message.chat
                    await set_group_language(chat)
                except Exception as e:
                    print(f"{e}")
                    pass
                try:
                    invitelink = await nexichat.export_chat_invite_link(message.chat.id)
                                                                        
                    link = f"[ɢᴇᴛ ʟɪɴᴋ]({invitelink})"
                except ChatAdminRequired:
                    link = "No Link"
                    
                try:
                    groups_photo = await nexichat.download_media(
                        chat.photo.big_file_id, file_name=f"chatpp{chat.id}.png"
                    )
                    chat_photo = (
                        groups_photo if groups_photo else "https://envs.sh/IL_.jpg"
                    )
                except AttributeError:
                    chat_photo = "https://envs.sh/IL_.jpg"
                except Exception as e:
                    pass

                count = await nexichat.get_chat_members_count(chat.id)
                chats = len(await get_served_chats())
                username = chat.username if chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐆ʀᴏᴜᴘ"
                msg = (
                    f"**📝𝐌ᴜsɪᴄ 𝐁ᴏᴛ 𝐀ᴅᴅᴇᴅ 𝐈ɴ 𝐀 #𝐍ᴇᴡ_𝐆ʀᴏᴜᴘ**\n\n"
                    f"**📌𝐂ʜᴀᴛ 𝐍ᴀᴍᴇ:** {chat.title}\n"
                    f"**🍂𝐂ʜᴀᴛ 𝐈ᴅ:** `{chat.id}`\n"
                    f"**🔐𝐂ʜᴀᴛ 𝐔sᴇʀɴᴀᴍᴇ:** @{username}\n"
                    f"**🖇️𝐆ʀᴏᴜᴘ 𝐋ɪɴᴋ:** {link}\n"
                    f"**📈𝐆ʀᴏᴜᴘ 𝐌ᴇᴍʙᴇʀs:** {count}\n"
                    f"**🤔𝐀ᴅᴅᴇᴅ 𝐁ʏ:** {message.from_user.mention}\n\n"
                    f"**ᴛᴏᴛᴀʟ ᴄʜᴀᴛs :** {chats}"
                )

                try:
                    OWNER = config.OWNER_ID
                    if OWNER:
                        await nexichat.send_photo(
                            int(OWNER_ID),
                            photo=chat_photo,
                            caption=msg,
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{message.from_user.first_name}", user_id=message.from_user.id)]]))
                                
                    
                except Exception as e:
                    print(f"Please Provide me correct owner id for send logs")
                    await nexichat.send_photo(
                        int(OWNER_ID),
                        photo=chat_photo,
                        caption=msg,
                        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"{message.from_user.first_name}", user_id=message.from_user.id)]]))
    except Exception as e:
        print(f"Err: {e}")


from pathlib import Path
import os
import time
import io

@nexichat.on_cmd(["ls"])
async def ls(_, m: Message):
    "To list all files and folders."

    cat = "".join(m.text.split(maxsplit=1)[1:])
    path = cat or os.getcwd()
    if not os.path.exists(path):
        await m.reply_text(
            f"There is no such directory or file with the name `{cat}`. Check again."
        )
        return

    path = Path(cat) if cat else os.getcwd()
    if os.path.isdir(path):
        if cat:
            msg = f"Folders and Files in `{path}`:\n"
        else:
            msg = "Folders and Files in Current Directory:\n"
        lists = os.listdir(path)
        files = ""
        folders = ""
        for contents in sorted(lists):
            catpath = os.path.join(path, contents)
            if not os.path.isdir(catpath):
                size = os.stat(catpath).st_size
                if str(contents).endswith((".mp3", ".flac", ".wav", ".m4a")):
                    files += f"🎵`{contents}`\n"
                elif str(contents).endswith((".opus")):
                    files += f"🎙`{contents}`\n"
                elif str(contents).endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
                    files += f"🎞`{contents}`\n"
                elif str(contents).endswith((".zip", ".tar", ".tar.gz", ".rar")):
                    files += f"🗜`{contents}`\n"
                elif str(contents).endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")):
                    files += f"🖼`{contents}`\n"
                else:
                    files += f"📄`{contents}`\n"
            else:
                folders += f"📁`{contents}`\n"
        msg = msg + folders + files if files or folders else f"{msg}__empty path__"
    else:
        size = os.stat(path).st_size
        msg = "The details of the given file:\n"
        if str(path).endswith((".mp3", ".flac", ".wav", ".m4a")):
            mode = "🎵"
        elif str(path).endswith((".opus")):
            mode = "🎙"
        elif str(path).endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
            mode = "🎞"
        elif str(path).endswith((".zip", ".tar", ".tar.gz", ".rar")):
            mode = "🗜"
        elif str(path).endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")):
            mode = "🖼"
        else:
            mode = "📄"
        time2 = time.ctime(os.path.getmtime(path))
        time3 = time.ctime(os.path.getatime(path))
        msg += f"**Location:** `{path}`\n"
        msg += f"**Icon:** `{mode}`\n"
        msg += f"**Size:** `{humanbytes(size)}`\n"
        msg += f"**Last Modified Time:** `{time2}`\n"
        msg += f"**Last Accessed Time:** `{time3}`"

    if len(msg) > 4096:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "ls.txt"
            await m.reply_document(
                out_file,
                caption=path,
            )
    else:
        await m.reply_text(msg)


@nexichat.on_cmd(["start", "aistart"])
async def start(_, m: Message):
    # Initializing the progress bar message
    baby = await m.reply_text(f"**▒▒▒▒▒▒▒▒▒▒ 0%**")
    
    # Simulating progress updates
    await baby.edit_text(f"**█▒▒▒▒▒▒▒▒▒ 10%**")
    await asyncio.sleep(0.5)
    await baby.edit_text(f"**██▒▒▒▒▒▒▒▒ 20%**")
    await asyncio.sleep(0.5)
    await baby.edit_text(f"**███▒▒▒▒▒▒▒ 30%**")
    await asyncio.sleep(0.5)
    await baby.edit_text(f"**████▒▒▒▒▒▒ 40%**")
    await asyncio.sleep(0.5)
    await baby.edit_text(f"**█████▒▒▒▒▒ 50%**")
    await asyncio.sleep(0.5)
    await baby.edit_text(f"**██████▒▒▒▒ 60%**")
    await asyncio.sleep(0.5)
    await baby.edit_text(f"**███████▒▒▒ 70%**")
    await asyncio.sleep(0.5)
    await baby.edit_text(f"**████████▒▒ 80%**")
    await asyncio.sleep(0.5)
    await baby.edit_text(f"**█████████▒ 90%**")
    await asyncio.sleep(0.5)
    await baby.edit_text(f"**██████████ 100%**")
    await asyncio.sleep(0.5)
    
    # After reaching 100%, notify the user and delete the progress message
    await baby.edit_text(f"**❖ ɴᴏᴡ sᴛᴀʀᴛᴇᴅ..**")
    await asyncio.sleep(0.5)
    await baby.delete()

    # Send the bot's default photo and stats
    chat_photo = BOT
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    UP, CPU, RAM, DISK = await bot_sys_stats()

    # Send bot stats to the user
    await m.reply_photo(
        photo=chat_photo, 
        caption=START.format(users, chats, UP), 
        reply_markup=InlineKeyboardMarkup(START_BOT)
    )
    
    await add_served_user(m.chat.id)

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"{m.chat.first_name}", user_id=m.chat.id)]])
    
    # Send bot photo to the owner
    await nexichat.send_photo(
        int(OWNER_ID), 
        photo=chat_photo, 
        caption=f"{m.from_user.mention} ʜᴀs sᴛᴀʀᴛᴇᴅ ʙᴏᴛ. \n\n**ɴᴀᴍᴇ :** {m.chat.first_name}\n**ᴜsᴇʀɴᴀᴍᴇ :** @{m.chat.username}\n**ɪᴅ :** {m.chat.id}\n\n**ᴛᴏᴛᴀʟ ᴜsᴇʀs :** {users}", 
        reply_markup=keyboard
    )
    
    await add_served_chat(m.chat.id)



@nexichat.on_cmd("help")
async def help(client: nexichat, m: Message):
    if m.chat.type == ChatType.PRIVATE:
        hmm = await m.reply_text(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTON),
        )

    else:
        await m.reply_text(
            text="**__Hᴇʏ, ᴘᴍ ᴍᴇ ғᴏʀ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅs__!**",
            reply_markup=InlineKeyboardMarkup(HELP_BUTN),
        )
        await add_served_chat(m.chat.id)



@nexichat.on_cmd("ping")
async def ping(_, message: Message):
    start = datetime.now()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    loda = await message.reply_text(
        text="ᴘɪɴɢɪɴɢ...",
    )

    ms = (datetime.now() - start).microseconds / 1000
    await loda.edit_text(
        text=f"**➥** `{ms}` ms\n**➲ ᴄᴘᴜ:** {CPU}\n**➲ ʀᴀᴍ:** {RAM}\n**➲ ᴅɪsᴋ:** {DISK}\n**➲ ᴜᴘᴛɪᴍᴇ »** {UP}\n\n<b>||**♡ Dᴇᴠᴇʟᴏᴘᴇʀ [˹ ʙᴀʙʏ-ᴍᴜsɪᴄ ™˼𓅂](https://t.me/BABY09_WORLD) **||</b>",
        reply_markup=InlineKeyboardMarkup(PNG_BTN),
    )
    if message.chat.type == ChatType.PRIVATE:
        await add_served_user(message.from_user.id)
    else:
        await add_served_chat(message.chat.id)


@nexichat.on_message(filters.command("stats"))
async def stats(cli: Client, message: Message):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    await message.reply_text(
        f"""```
{(await cli.get_me()).mention} ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛs:```
➥ **ᴄʜᴀᴛs :** {chats}
➥ **ᴜsᴇʀs :** {users}"""
    )


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTO_SLEEP = 5
IS_BROADCASTING = False
broadcast_lock = asyncio.Lock()


@nexichat.on_message(
    filters.command(["broadcast", "gcast"]) & filters.user(int(OWNER_ID))
)
async def broadcast_message(client, message):
    global IS_BROADCASTING
    async with broadcast_lock:
        if IS_BROADCASTING:
            return await message.reply_text(
                "❍ Bʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ ᴡᴀɪᴛ ғᴏʀ ᴄᴏᴍᴘʟᴇᴛᴇ."
            )

        IS_BROADCASTING = True
        try:
            query = message.text.split(None, 1)[1].strip()
        except IndexError:
            query = message.text.strip()
        except Exception as eff:
            return await message.reply_text(
                f"**Error**: {eff}"
            )
        try:
            if message.reply_to_message:
                broadcast_content = message.reply_to_message
                broadcast_type = "reply"
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }
            else:
                if len(message.command) < 2:
                    return await message.reply_text(
                        "**❍ ᴇxᴀᴍᴘʟᴇ :**\n\n❍ /broadcast [ᴍᴇssᴀɢᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ]"
                    )
                
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }

                for flag in flags:
                    query = query.replace(flag, "").strip()

                if not query:
                    return await message.reply_text(
                        "❍ Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴠᴀʟɪᴅ ᴛᴇxᴛ ᴍᴇssᴀɢᴇ ᴏʀ ᴀ ғʟᴀɢ: -pin, -nogroup, -pinloud, -user"
                    )

                
                broadcast_content = query
                broadcast_type = "text"
            

            await message.reply_text("**➥ Bʀᴏᴀᴅᴄᴀsᴛ ʀᴜɴɪɴɢ...**")

            if not flags.get("-nogroup", False):
                sent = 0
                pin_count = 0
                chats = await get_served_chats()

                for chat in chats:
                    chat_id = int(chat["chat_id"])
                    if chat_id == message.chat.id:
                        continue
                    try:
                        if broadcast_type == "reply":
                            m = await nexichat.forward_messages(
                                chat_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await nexichat.send_message(
                                chat_id, text=broadcast_content
                            )
                        sent += 1

                        if flags.get("-pin", False) or flags.get("-pinloud", False):
                            try:
                                await m.pin(
                                    disable_notification=flags.get("-pin", False)
                                )
                                pin_count += 1
                            except Exception as e:
                                continue

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for chat {chat_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping chat {chat_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        
                        continue

                await message.reply_text(
                    f"**➬ Bʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ {sent} ᴄʜᴀᴛs ᴀɴᴅ ᴘɪɴɴᴇᴅ ɪɴ {pin_count} ᴄʜᴀᴛs.**"
                )

            if flags.get("-user", False):
                susr = 0
                users = await get_served_users()

                for user in users:
                    user_id = int(user["user_id"])
                    try:
                        if broadcast_type == "reply":
                            m = await nexichat.forward_messages(
                                user_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await nexichat.send_message(
                                user_id, text=broadcast_content
                            )
                        susr += 1

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for user {user_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping user {user_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        
                        continue

                await message.reply_text(f"**➬ Bʀᴏᴀᴅᴄᴀsᴛ ᴛᴏ {susr} ᴜsᴇʀ.**")

        finally:
            IS_BROADCASTING = False


