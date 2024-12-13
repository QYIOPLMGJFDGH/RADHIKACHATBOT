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
    """Check if the message is unwanted based on certain prefixes."""
    return message.text.startswith(("!", "/", "?", "@", "#"))

async def handle_chatbot_response(client: Client, message: Message, word: str):
    """Handle the chatbot response logic."""
    try:
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
            
            # If replying to a message from someone else, add new data to DB
            if message.reply_to_message.from_user.id != client.id:
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
        # Optionally, notify the user if an error occurs
        if message.chat.type != "private":
            await message.reply_text("An error occurred while processing your request.")

# Handle chat messages for text or stickers in group chats
@shizuchat.on_message((filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot)
async def chatbot_response(client: Client, message: Message):
    """Process incoming messages and reply with chatbot response."""
    try:
        if is_unwanted_message(message):
            return
        word = message.text if message.text else message.sticker.file_unique_id
        await handle_chatbot_response(client, message, word)
    except Exception as e:
        LOGGER.error(f"Error in chatbot_response: {e}")

# Private chat response logic (for private chats)
@shizuchat.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
async def vickprivate(client: Client, message: Message):
    """Process messages in private chat."""
    try:
        if not message.reply_to_message:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            word = message.text if message.text else message.sticker.file_unique_id
            await handle_chatbot_response(client, message, word)
    except Exception as e:
        LOGGER.error(f"Error in vickprivate: {e}")

# Optional: Test to verify ChatAction.TYPING is working in isolation
@shizuchat.on_message(filters.text)
async def test_typing_action(client: Client, message: Message):
    """Test if typing action works without any additional logic."""
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(2)  # Simulate delay
        await message.reply_text("Hello, I'm typing!")
    except Exception as e:
        LOGGER.error(f"Error in test_typing_action: {e}")
