import random
import psutil
import time
from nexichat import _boot_
from nexichat import get_readable_time
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from deep_translator import GoogleTranslator
from nexichat.database.chats import get_served_chats, add_served_chat
from nexichat.database.users import get_served_users, add_served_user
from config import MONGO_URL
from nexichat import nexichat, mongo
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery
import asyncio
import config
from nexichat import LOGGER, nexichat, db
from nexichat.mplugin.helpers import chatai
from nexichat.mplugin.helpers import (
    ADMIN_READ,
    START_BOT,
    BACK,
    CHATBOT_BACK,
    CHATBOT_READ,
    DEV_OP,
    HELP_BTN,
    HELP_READ,
    MUSIC_BACK_BTN,
    START,
    TOOLS_DATA_READ,
    languages,
)


mongo_client = MongoClient(MONGO_URL)
chatbot_db = mongo_client["VickDb"]["Vick"]  # Stores chatbot status (enabled/disabled)
word_db = mongo_client["Word"]["WordDb"]     # Stores word-response pairs
user_status_db = mongo_client["UserStatus"]["UserDb"]  # Stores user status
user_status_db = mongo_client["UserStatus"]["UserDb"]  # User-specific status
locked_words_db = mongo_client["LockedWords"]["LockedWordsDb"]
BOT_OWNER_ID = 7400383704
lang_db = db.ChatLangDb.LangCollection
status_db = db.chatbot_status_db.status

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

# Fetch dynamic START_TEXT
async def fetch_data():
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    UP, CPU, RAM, DISK = await bot_sys_stats()  # Assuming bot_sys_stats is defined elsewhere
    
    # Ensure START string has the correct number of placeholders
    try:
        START_TEXT = START.format(users, chats, UP)  # Format the START text with dynamic data
    except IndexError:
        LOGGER.error("Error in START text formatting. Make sure the START string has enough placeholders.")
        START_TEXT = "Error: Could not generate dynamic START text."
        
    return START_TEXT


@nexichat.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    try:
        LOGGER.info(query.data)

        # Fetch START_TEXT dynamically
        START_TEXT = await fetch_data()

        # Handle HELP callback
        if query.data == "HELP":
            await query.message.edit_text(
                text=HELP_READ,
                reply_markup=InlineKeyboardMarkup(HELP_BTN),
                disable_web_page_preview=True,
            )

        # Parse callback data for word locking
        elif ":" in query.data and len(query.data.split(":")) == 3:
            action, word_to_lock, user_id = query.data.split(":")
            user_id = int(user_id)

            if query.from_user.id == BOT_OWNER_ID:
                if action == "accept":
                    # Lock the word
                    locked_words_db.update_one(
                        {"word": word_to_lock},
                        {"$set": {"word": word_to_lock}},
                        upsert=True
                    )

                    # Update callback message
                    await query.message.edit_text(
                        text=f"✅ The word '{word_to_lock}' has been locked."
                    )

                    # Notify the user
                    await client.send_message(
                        chat_id=user_id,
                        text=f"Your request to lock the word '{word_to_lock}' has been **accepted** by the bot owner."
                    )

                elif action == "decline":
                    # Update callback message
                    await query.message.edit_text(
                        text=f"❌ The request to lock '{word_to_lock}' has been declined."
                    )

                    # Notify the user
                    await client.send_message(
                        chat_id=user_id,
                        text=f"Your request to lock the word '{word_to_lock}' has been **declined** by the bot owner."
                    )

                # Acknowledge the callback query
                await query.answer()
            else:
                # Unauthorized user clicks the button
                await query.answer("You are not authorized to perform this action.", show_alert=True)

        # Handle CLOSE callback
        elif query.data == "CLOSE":
            await query.message.delete()
            await query.answer("Closed menu!", show_alert=True)

        # Go back to the main menu
        elif query.data == "BACK":
            await query.message.edit_text(
                text=START_TEXT,
                reply_markup=InlineKeyboardMarkup(DEV_OP),
            )

        # Admin information
        elif query.data == "ADMINS":
            await query.message.edit_text(
                text=ADMIN_READ,
                reply_markup=InlineKeyboardMarkup(MUSIC_BACK_BTN),
            )

        # Tools information
        elif query.data == "TOOLS_DATA":
            await query.message.edit_text(
                text=TOOLS_DATA_READ,
                reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
            )

        # Back to the help menu
        elif query.data == "BACK_HELP":
            await query.message.edit_text(
                text=HELP_READ,
                reply_markup=InlineKeyboardMarkup(HELP_BTN),
            )

        # Chatbot commands
        elif query.data == "CHATBOT_CMD":
            await query.message.edit_text(
                text=CHATBOT_READ,
                reply_markup=InlineKeyboardMarkup(CHATBOT_BACK),
            )

        # Back to chatbot menu
        elif query.data == "CHATBOT_BACK":
            await query.message.edit_text(
                text=HELP_READ,
                reply_markup=InlineKeyboardMarkup(HELP_BTN),
            )

        # Back to home menu
        elif query.data == "HOME_BACK":
            await query.message.edit_text(
                text=START_TEXT,
                reply_markup=InlineKeyboardMarkup(START_BOT),
            )
    except Exception as e:
        LOGGER.error(f"Error handling callback: {e}")
        await query.answer("An error occurred while processing the request.", show_alert=True)
