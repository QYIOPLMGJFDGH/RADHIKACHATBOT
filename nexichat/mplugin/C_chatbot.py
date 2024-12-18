import os
import re
import asyncio
import logging
import time
import config
from nexichat import _boot_
from nexichat import get_readable_time
import psutil
import random
from pyrogram.enums import ChatType
from pyrogram.errors import FloodWait, ChatAdminRequired
from nexichat import mongo
from datetime import datetime
from nexichat.mplugin.helpers import is_owner
from nexichat.database.chats import get_served_chats, add_served_chat
from nexichat.database.users import get_served_users, add_served_user
from config import MONGO_URL
from config import OWNER_ID, MONGO_URL, OWNER_USERNAME
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageIdInvalid, ChatAdminRequired, EmoticonInvalid, ReactionInvalid
from random import choice
from pyrogram import Client, filters
from nexichat import CLONE_OWNERS
from nexichat.mplugin.Callback import cb_handler
from pyrogram.types import CallbackQuery
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ChatAction
from nexichat import db
from pymongo import MongoClient
from nexichat.mplugin.helpers import (
    START,
    START_BOT,
    PNG_BTN,
    CLOSE_BTN,
    HELP_BTN,
    HELP_BUTN,
    HELP_READ,
    HELP_START,
)

# MongoDB Initialization
mongo_client = MongoClient(MONGO_URL)
chatbot_db = mongo_client["VickDb"]["Vick"]  # Stores chatbot status (enabled/disabled)
word_db = mongo_client["Word"]["WordDb"]     # Stores word-response pairs
user_status_db = mongo_client["UserStatus"]["UserDb"]  # Stores user status
locked_words_db = mongo_client["LockedWords"]["LockedWordsDb"]
user_status_db = mongo_client["UserStatus"]["UserDb"]  # User-specific status
chatai = db.Word.WordDb
lang_db = db.ChatLangDb.LangCollection
status_db = db.ChatBotStatusDb.StatusCollection
BOT_OWNER_ID = 7400383704

GSTART = """**ʜᴇʏ ᴅᴇᴀʀ {}**\n\n**ᴛʜᴀɴᴋs ғᴏʀ sᴛᴀʀᴛ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ʟᴀɴɢᴜᴀɢᴇ ʙʏ ᴄʟɪᴄᴋ ᴏɴ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs.**\n**ᴄʟɪᴄᴋ ᴀɴᴅ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ғᴀᴠᴏᴜʀɪᴛᴇ ʟᴀɴɢᴜᴀɢᴇ ᴛᴏ sᴇᴛ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ ғᴏʀ ʙᴏᴛ ʀᴇᴘʟʏ.**\n\n**ᴛʜᴀɴᴋ ʏᴏᴜ ᴘʟᴇᴀsᴇ ᴇɴɪᴏʏ.**"""
BOT = "https://files.catbox.moe/hwqq2e.jpg"


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

@Client.on_message(filters.command("help"))
async def help(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        hmm = await message.reply_text(
            text=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )
    else:
        await message.reply_text(
            text="**__Hᴇʏ, ᴘᴍ ᴍᴇ ғᴏʀ ʜᴇʟᴘ ᴄᴏᴍᴍᴀɴᴅs__!**",
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )
        await add_served_chat(message.chat.id)



@Client.on_message(filters.command("ping"))
async def ping(client: Client, message: Message):
    start = datetime.now()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    loda = await message.reply_text(
        text="ᴘɪɴɢɪɴɢ...",
    )

    ms = (datetime.now() - start).microseconds / 1000
    await loda.edit_text(
        text=f"**➥** `{ms}` ms\n**➲ ᴄᴘᴜ:** {CPU}\n**➲ ʀᴀᴍ:** {RAM}\n**➲ ᴅɪsᴋ:** {DISK}\n**➲ ᴜᴘᴛɪᴍᴇ »** {UP}\n\n<b>||**♡ Dᴇᴠᴇʟᴏᴘᴇʀ ˹ ʙᴀʙʏ-ᴍᴜsɪᴄ ™˼𓅂**||</b>",
        reply_markup=InlineKeyboardMarkup(PNG_BTN),
    )
    if message.chat.type == ChatType.PRIVATE:
        await add_served_user(message.from_user.id)
    else:
        await add_served_chat(message.chat.id)


@Client.on_message(filters.command("stats"))
async def stats(cli: Client, message: Message):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    await message.reply_text(
        f"""```
{(await cli.get_me()).mention} ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛs:```
➥ **ᴄʜᴀᴛs :** {chats}
➥ **ᴜsᴇʀs :** {users}"""
    )


@Client.on_message(filters.command(["start", "aistart"]))
async def sotart(client: Client, m: Message):
    # Get number of users and chats
    users = len(await get_served_users())
    chats = len(await get_served_chats())

    if m.chat.type == ChatType.PRIVATE:
        # Send the progress bar message
        baby = await m.reply_text(f"**▒▒▒▒▒▒▒▒▒▒ 0%**")
        
        # Simulate progress updates with progress bar
        await baby.edit_text(f"**█▒▒▒▒▒▒▒▒▒ 10%**")
        await asyncio.sleep(0.005)
        await baby.edit_text(f"**██▒▒▒▒▒▒▒▒ 20%**")
        await asyncio.sleep(0.005)
        await baby.edit_text(f"**███▒▒▒▒▒▒▒ 30%**")
        await asyncio.sleep(0.005)
        await baby.edit_text(f"**████▒▒▒▒▒▒ 40%**")
        await asyncio.sleep(0.005)
        await baby.edit_text(f"**█████▒▒▒▒▒ 50%**")
        await asyncio.sleep(0.005)
        await baby.edit_text(f"**██████▒▒▒▒ 60%**")
        await asyncio.sleep(0.005)
        await baby.edit_text(f"**███████▒▒▒ 70%**")
        await asyncio.sleep(0.005)
        await baby.edit_text(f"**████████▒▒ 80%**")
        await asyncio.sleep(0.005)
        await baby.edit_text(f"**█████████▒ 90%**")
        await asyncio.sleep(0.005)
        await baby.edit_text(f"**██████████ 100%**")
        await asyncio.sleep(0.005)
        
        # After reaching 100%, notify the user and delete the progress message
        await baby.edit_text(f"**❖ ɴᴏᴡ sᴛᴀʀᴛᴇᴅ..**")
        await asyncio.sleep(0.5)
        await baby.delete()

        # Set default photo (BOT) in case of no user photo
        chat_photo = BOT  # Default photo is set to your bot's image

        # Send the bot's stats to the user
        users = len(await get_served_users())
        chats = len(await get_served_chats())
        UP, CPU, RAM, DISK = await bot_sys_stats()

        await m.reply_text(
            text=START.format(users, chats, UP),
            reply_markup=InlineKeyboardMarkup(START_BOT)
        )

        # Log the user interaction
        await add_served_user(m.chat.id)

        # Create a keyboard to mention the user
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"{m.chat.first_name}", user_id=m.chat.id)]])

        # Notify the owner about the new user interaction
        bot_id = client.me.id
        owner_id = CLONE_OWNERS.get(bot_id)
        if owner_id:
            await client.send_message(
                int(owner_id),
                caption=f"{m.from_user.mention} ʜᴀs sᴛᴀʀᴛᴇᴅ ʙᴏᴛ. \n\n**ɴᴀᴍᴇ :** {m.chat.first_name}\n**ᴜsᴇʀɴᴀᴍᴇ :** @{m.chat.username}\n**ɪᴅ :** {m.chat.id}\n\n**ᴛᴏᴛᴀʟ ᴜsᴇʀs :** {users}",
                reply_markup=keyboard
            )
        
    else:
        # Handle the case for groups/chats other than private chats
        await m.reply_text(
            text=GSTART.format(m.from_user.mention or "can't mention"),
            reply_markup=InlineKeyboardMarkup(HELP_START),
        )
        await add_served_chat(m.chat.id)



@Client.on_message(filters.new_chat_members)
async def welcomejej(client, message: Message):
    chat = message.chat
    await add_served_chat(message.chat.id)
    await set_default_status(message.chat.id)
    
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    
    try:
        for member in message.new_chat_members:
            bot_info = await client.get_me()
            
            # Ensure bot_info is not None before accessing .id
            if bot_info and member.id == bot_info.id:
                try:
                    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("sᴇʟᴇᴄᴛ ʟᴀɴɢᴜᴀɢᴇ", callback_data="choose_lang")]])    
                    await message.reply_text(text=START.format(users, chats), reply_markup=reply_markup)
                except Exception as e:
                    print(f"{e}")
                    pass
                
                try:
                    # Try exporting chat invite link and handle the case where it may not be available
                    try:
                        invitelink = await client.export_chat_invite_link(message.chat.id)
                        link = f"[ɢᴇᴛ ʟɪɴᴋ]({invitelink})"
                    except ChatAdminRequired:
                        link = "No Link"
                    except Exception as e:
                        print(f"Error generating invite link: {e}")
                        link = "No Link"
                except Exception as e:
                    print(f"Error getting invite link: {e}")
                    link = "No Link"
                
                # Handle chat photo download with appropriate checks
                try:
                    if chat.photo and chat.photo.big_file_id:
                        groups_photo = await client.download_media(
                            chat.photo.big_file_id, file_name=f"chatpp{chat.id}.png"
                        )
                        chat_photo = groups_photo if groups_photo else "https://envs.sh/IL_.jpg"
                    else:
                        chat_photo = "https://envs.sh/IL_.jpg"
                except Exception as e:
                    print(f"Error downloading group photo: {e}")
                    chat_photo = "https://envs.sh/IL_.jpg"

                # Prepare group info message
                count = await client.get_chat_members_count(chat.id)
                username = chat.username if chat.username else "𝐏ʀɪᴠᴀᴛᴇ 𝐆ʀᴏᴜᴩ"
                msg = (
                    f"**📝𝐁ᴏᴛ 𝐀ᴅᴅᴇᴅ 𝐈ɴ 𝐀 #𝐍ᴇᴡ_𝐆ʀᴏᴜᴘ**\n\n"
                    f"**📌𝐂ʜᴀᴛ 𝐍ᴀᴍᴇ:** {chat.title}\n"
                    f"**🍂𝐂ʜᴀᴛ 𝐈ᴅ:** `{chat.id}`\n"
                    f"**🔐𝐂ʜᴀᴛ 𝐔sᴇʀɴᴀᴍᴇ:** @{username}\n"
                    f"**🖇️𝐆ʀᴏᴜᴘ 𝐋ɪɴᴋ:** {link}\n"
                    f"**📈𝐆ʀᴏᴜᴘ 𝐌ᴇᴍʙᴇʀs:** {count}\n"
                    f"**🤔𝐀ᴅᴅᴇᴅ 𝐁ʏ:** {message.from_user.mention}\n\n"
                    f"**ᴛᴏᴛᴀʟ ᴄʜᴀᴛs :** {chats}"
                )

                # Send the group info to the bot owner using send_message
                try:
                    bot_id = client.me.id
                    owner_id = CLONE_OWNERS.get(bot_id)
                    
                    if owner_id:
                        await client.send_message(
                            int(owner_id),
                            text=msg,
                            reply_markup=InlineKeyboardMarkup(
                                [[InlineKeyboardButton(f"{message.from_user.first_name}", user_id=message.from_user.id)]]
                            )
                        )
                except Exception as e:
                    print(f"Err sending message to owner: {e}")
                    
    except Exception as e:
        print(f"Error in welcomejej: {e}")


# Command to disable the chatbot (works for all users in both private and group chats)
@Client.on_message(filters.command(["chatbot off"], prefixes=["/"]))
async def chatbot_off(client, message: Message):
    chat_id = message.chat.id

    # Disable the chatbot by updating the database
    chatbot_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"status": "disabled"}},
        upsert=True
    )

    # If it's a private chat, update the user status in the database
    if message.chat.type == "private":
        user_id = message.from_user.id
        user_status_db.update_one(
            {"user_id": user_id},
            {"$set": {"status": "disabled", "chat_id": chat_id}},
            upsert=True
        )
        await message.reply_text("Cʜᴀᴛʙᴏᴛ ᴍᴏᴅᴇ ᴅɪsᴀʙʟᴇ!")
    else:
        await message.reply_text("Cʜᴀᴛʙᴏᴛ ᴍᴏᴅᴇ ᴅɪsᴀʙʟᴇ!")

# Command to enable the chatbot (works in both private and group chats)
@Client.on_message(filters.command(["chatbot on"], prefixes=["/"]))
async def chatbot_on(client, message: Message):
    chat_id = message.chat.id

    # Enable the chatbot by updating the database
    chatbot_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"status": "enabled"}},
        upsert=True
    )

    # If it's a private chat, update the user status in the database
    if message.chat.type == "private":
        user_id = message.from_user.id
        user_status_db.update_one(
            {"user_id": user_id},
            {"$set": {"status": "enabled", "chat_id": chat_id}},
            upsert=True
        )
        await message.reply_text("Cʜᴀᴛʙᴏᴛ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇ!")
    else:
        await message.reply_text("Cʜᴀᴛʙᴏᴛ ᴍᴏᴅᴇ ᴇɴᴀʙʟᴇ!")

# Command to display chatbot status (on/off) in private and group chats
@Client.on_message(filters.command(["chatbot"], prefixes=["/"]))
async def chatbot_usage(client, message: Message):
    chat_id = message.chat.id

    # Fetch chatbot status from the database
    chatbot_status = chatbot_db.find_one({"chat_id": chat_id})
    if chatbot_status and chatbot_status.get("status") == "enabled":
        status_message = "Chatbot is currently **enabled**."
    else:
        status_message = "Chatbot is currently **disabled**."

    # Handle the message depending on whether it's in a private chat or a group chat
    if message.chat.type == "private":
        # Private chat
        await message.reply_text(f"**Sᴛᴀᴛᴜs ➟** {status_message}\n\n**𝐂ᴏᴍᴍᴀɴᴅ ᴏɴ ⇮ ᴏғғ**!\n-`/chatbot on` - ᴛᴏ ᴇɴᴀʙʟᴇ\n`/chatbot off` - ᴛᴏ ᴅɪsᴀʙʟᴇ.")
    else:
        # Group chat
        await message.reply_text(f"**Sᴛᴀᴛᴜs ➟** {status_message}\n\n**𝐂ᴏᴍᴍᴀɴᴅ ᴏɴ ⇮ ᴏғғ**!\n-`/chatbot on` - ᴛᴏ ᴇɴᴀʙʟᴇ\n`/chatbot off` - ᴛᴏ ᴅɪsᴀʙʟᴇ.")


# Regular expression to filter unwanted messages containing special characters like /, !, ?, ~, \
UNWANTED_MESSAGE_REGEX = r"^[\W_]+$|[\/!?\~\\]"



# Command to request word lock (Owner Only)
@Client.on_message(filters.command("lock", prefixes=["/"]))
async def lock_word_request(client, message: Message):
    # Extract the word after '/lock' command
    parts = message.text.split()

    # If the word is missing (after the command), handle the case
    if len(parts) == 1:
        await message.reply_text("Tʜɪs ғᴜᴛᴜʀᴇs ᴏɴʟʏ ᴡᴏʀᴋ ɪɴ [ᴍᴀɪɴ ʙᴏᴛ](https://t.me/RADHIKA_CHAT_RROBOT)")
    else:
        word_to_lock = parts[1]
        await message.reply_text(f"Gᴏ ᴛᴏ [ᴍᴀɪɴ ʙᴏᴛ](https://t.me/RADHIKA_CHAT_RROBOT) ᴀɴᴅ sᴇɴᴅ `/lock {word_to_lock}`")


@Client.on_message(filters.command("clone", prefixes=["/"]))
async def clone_request(client, message: Message):
    # Extract the word after '/lock' command
    parts = message.text.split()

    # If the word is missing (after the command), handle the case
    if len(parts) == 1:
        await message.reply_text("Tʜɪs ғᴜᴛᴜʀᴇs ᴏɴʟʏ ᴡᴏʀᴋ ɪɴ [ᴍᴀɪɴ ʙᴏᴛ](https://t.me/RADHIKA_CHAT_RROBOT)")
    else:
        word_to_lock = parts[1]
        await message.reply_text(f"Gᴏ ᴛᴏ [ᴍᴀɪɴ ʙᴏᴛ](https://t.me/RADHIKA_CHAT_RROBOT) ᴀɴᴅ sᴇɴᴅ `/clone {word_to_lock}` ᴛᴏ ᴄʟᴏɴᴇ ʏᴏᴜʀ ʙᴏᴛ")

# Callback handler for Accept/Decline actions

# Chatbot responder for group chats
@Client.on_message((filters.text | filters.sticker) & ~filters.private & ~filters.bot)
async def chatbot_responder(client: Client, message: Message):
    if message.text and re.match(UNWANTED_MESSAGE_REGEX, message.text):
        return

    chat_id = message.chat.id

    chatbot_status = chatbot_db.find_one({"chat_id": chat_id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

    locked_word = locked_words_db.find_one({"word": message.text})
    if locked_word:
        return  # Don't reply if the word is locked

    await client.send_chat_action(chat_id, ChatAction.TYPING)

    if not message.reply_to_message:
        responses = list(word_db.find({"word": message.text}))
        if responses:
            response = random.choice(responses)
            if response["check"] == "sticker":
                await message.reply_sticker(response["text"])
            else:
                await message.reply_text(response["text"])
    else:
        reply = message.reply_to_message
        if reply.from_user.id == (await app.get_me()).id:
            responses = list(word_db.find({"word": message.text}))
            if responses:
                response = random.choice(responses)
                if response["check"] == "sticker":
                    await message.reply_sticker(response["text"])
                else:
                    await message.reply_text(response["text"])
        else:
            if message.text:
                word_db.insert_one({"word": reply.text, "text": message.text, "check": "text"})
            elif message.sticker:
                word_db.insert_one({"word": reply.text, "text": message.sticker.file_id, "check": "sticker"})


# Function to sanitize input to prevent errors caused by special characters
def sanitize_input(word):
    return re.sub(r'[^A-Za-z0-9\s]', '', word)


# Chatbot responder for private chats
@Client.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
async def chatbot_private(client: Client, message: Message):
    if re.match(UNWANTED_MESSAGE_REGEX, message.text):
        return

    chatbot_status = chatbot_db.find_one({"chat_id": message.chat.id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

    locked_word = locked_words_db.find_one({"word": message.text})
    if locked_word:
        return  # Don't reply if the word is locked

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)

    if not message.reply_to_message:
        responses = list(word_db.find({"word": message.text}))
        if responses:
            response = random.choice(responses)
            if response["check"] == "sticker":
                await message.reply_sticker(response["text"])
            else:
                await message.reply_text(response["text"])
    else:
        reply = message.reply_to_message
        if reply.from_user.id == (await app.get_me()).id:
            responses = list(word_db.find({"word": message.text}))
            if responses:
                response = random.choice(responses)
                if response["check"] == "sticker":
                    await message.reply_sticker(response["text"])
                else:
                    await message.reply_text(response["text"])
        else:
            if message.text:
                word_db.insert_one({"word": reply.text, "text": message.text, "check": "text"})
            elif message.sticker:
                word_db.insert_one({"word": reply.text, "text": message.sticker.file_id, "check": "sticker"})


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTO_SLEEP = 5
IS_BROADCASTING = False
broadcast_lock = asyncio.Lock()


@Client.on_message(filters.command(["broadcast", "gcast"]))
async def cbroadcast_message(client, message):
    global IS_BROADCASTING
    bot_id = (await client.get_me()).id
    user_id = message.from_user.id
    owner_check = is_owner(client, user_id)

    if owner_check is not True:
        await message.reply_text(owner_check)
        return
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
                        "**Please provide text after the command or reply to a message for broadcasting.**"
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
                        "**❍ ᴇxᴀᴍᴘʟᴇ :**\n\n❍ /broadcast [ᴍᴇssᴀɢᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ]"
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
                            m = await client.forward_messages(
                                chat_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await client.send_message(
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
                            m = await client.forward_messages(
                                user_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await client.send_message(
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


    
