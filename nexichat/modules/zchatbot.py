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
from nexichat import mongo, db, LOGGER, nexichat as shizuchat

# Single MongoDB connection instance
client_db = MongoClient(config.MONGO_URL)
chatai = client_db["Word"]["WordDb"]
vick_db = client_db["VickDb"]["Vick"]

def is_unwanted_message(message: Message) -> bool:
    return message.text.startswith(("!", "/", "?", "@", "#"))

# Helper function to handle database queries and responses
async def handle_chatbot_response(client: Client, message: Message, word: str):
    # Check if there is a reply to the message
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

    # Handle reply messages
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
            # Inserting new word-text pair if not found
            if message.text:
                is_chat = chatai.find_one({"word": message.reply_to_message.text, "text": message.text})
                if not is_chat:
                    chatai.insert_one({"word": message.reply_to_message.text, "text": message.text, "check": "none"})
            if message.sticker:
                is_chat = chatai.find_one({"word": message.reply_to_message.text, "id": message.sticker.file_unique_id})
                if not is_chat:
                    chatai.insert_one({"word": message.reply_to_message.text, "text": message.sticker.file_id, "check": "sticker", "id": message.sticker.file_unique_id})

# Handle chat messages for text or stickers
@shizuchat.on_message((filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot)
async def chatbot_response(client: Client, message: Message):
    try:
        if is_unwanted_message(message):
            return
    except Exception as e:
        LOGGER.error(f"Error in chatbot_response: {e}")
    
    word = message.text if message.text else message.sticker.file_unique_id
    await handle_chatbot_response(client, message, word)

# Private chat response
@shizuchat.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
async def vickprivate(client: Client, message: Message):
    if not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        word = message.text if message.text else message.sticker.file_unique_id
        await handle_chatbot_response(client, message, word)
