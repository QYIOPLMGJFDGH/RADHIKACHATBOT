import random
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus as CMS
import asyncio
import config
from nexichat import nexichat
from nexichat import mongo, db, LOGGER, nexichat as shizuchat

# Single MongoDB connection instance
client_db = MongoClient(config.MONGO_URL)
chatai = client_db["Word"]["WordDb"]
vick_db = client_db["VickDb"]["Vick"]
status_db = client_db["StatusDb"]["ChatStatus"]  # Assuming you're using this to store chat statuses.

CHATBOT_ON = [
    [
        InlineKeyboardButton(text="ᴇɴᴀʙʟᴇ", callback_data="enable_chatbot"),
        InlineKeyboardButton(text="ᴅɪsᴀʙʟᴇ", callback_data="disable_chatbot"),
    ],
]

@nexichat.on_message(filters.command("chatbot"))
async def chatbot_command(client: Client, message: Message):
    """Handle /chatbot command to show inline buttons for enabling/disabling chatbot."""
    await message.reply_text(
        f"Chat: {message.chat.title}\n**Choose an option to enable/disable the chatbot.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )

@nexichat.on_callback_query(filters.regex("enable_chatbot|disable_chatbot"))
async def toggle_chatbot(client: Client, query: CallbackQuery):
    """Handle callback queries for enabling/disabling the chatbot."""
    chat_id = query.message.chat.id
    action = query.data  # This will be either 'enable_chatbot' or 'disable_chatbot'

    if action == "enable_chatbot":
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "enabled"}}, upsert=True)
        await query.answer("Cʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇ ✅", show_alert=True)
        await query.edit_message_text(
            f"Chat: {query.message.chat.title}\n**ᴄʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ.**"
        )

    elif action == "disable_chatbot":
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "disabled"}}, upsert=True)
        await query.answer("ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇ ✅", show_alert=True)
        await query.edit_message_text(
            f"Chat: {query.message.chat.title}\n**ᴄʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.**"
        )

# Helper function to check unwanted messages
def is_unwanted_message(message: Message) -> bool:
    return message.text.startswith(("!", "/", "?", "@", "#"))

# Helper function to handle chatbot responses (reply with text or sticker)
async def handle_chatbot_response(client: Client, message: Message, word: str):
    try:
        if not message.reply_to_message:
            is_vick = vick_db.find_one({"chat_id": message.chat.id})
            if not is_vick:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                K = [x["text"] for x in chatai.find({"word": word})]
                if K:
                    hey = random.choice(K)
                    is_text = chatai.find_one({"text": hey})
                    if is_text["check"] == "sticker":
                        await message.reply_sticker(hey)
                    else:
                        await message.reply_text(hey)

        elif message.reply_to_message:
            is_vick = vick_db.find_one({"chat_id": message.chat.id})
            
            if message.reply_to_message.from_user.id == client.id and not is_vick:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                K = [x["text"] for x in chatai.find({"word": word})]
                if K:
                    hey = random.choice(K)
                    is_text = chatai.find_one({"text": hey})
                    if is_text["check"] == "sticker":
                        await message.reply_sticker(hey)
                    else:
                        await message.reply_text(hey)
            
            if message.reply_to_message.from_user.id != client.id:
                # Insert new word-text pair if not found
                if message.text:
                    is_chat = chatai.find_one({"word": message.reply_to_message.text, "text": message.text})
                    if not is_chat:
                        chatai.insert_one({"word": message.reply_to_message.text, "text": message.text, "check": "none"})
                if message.sticker:
                    is_chat = chatai.find_one({"word": message.reply_to_message.text, "id": message.sticker.file_unique_id})
                    if not is_chat:
                        chatai.insert_one({"word": message.reply_to_message.text, "text": message.sticker.file_id, "check": "sticker", "id": message.sticker.file_unique_id})

    except Exception as e:
        LOGGER.error(f"Error in handle_chatbot_response: {e}")

# Handle chat messages for text or stickers in group chats
@shizuchat.on_message((filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot)
async def chatbot_response(client: Client, message: Message):
    try:
        if is_unwanted_message(message):
            return
        word = message.text if message.text else message.sticker.file_unique_id
        await handle_chatbot_response(client, message, word)
    except Exception as e:
        LOGGER.error(f"Error in chatbot_response: {e}")

# Private chat response (handling private messages)
@shizuchat.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
async def vickprivate(client: Client, message: Message):
    if not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        word = message.text if message.text else message.sticker.file_unique_id
        await handle_chatbot_response(client, message, word)
