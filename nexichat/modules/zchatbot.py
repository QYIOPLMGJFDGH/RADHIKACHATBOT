import random
import asyncio
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
status_db = client_db["StatusDb"]["ChatStatus"]  # Chat status collection for enabling/disabling

# Handle the /chatbot command to enable or disable the chatbot
@nexichat.on_message(filters.command("chatbot"))
async def chatbot_command(client: Client, message: Message):
    """Handle /chatbot command to enable/disable chatbot."""
    # Check if the message is "/chatbot on" or "/chatbot off"
    if len(message.command) > 1:
        command = message.command[1].lower()  # Get the second part of the command
    else:
        command = ''

    if command == "on":
        # Enable the chatbot for the chat
        chat_id = message.chat.id
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "enabled"}}, upsert=True)
        
        # Send confirmation message
        await message.reply_text(
            f"Chat: {message.chat.title}\n**Chatbot has been enabled.**"
        )
        
    elif command == "off":
        # Disable the chatbot for the chat
        chat_id = message.chat.id
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "disabled"}}, upsert=True)

        # Send confirmation message
        await message.reply_text(
            f"Chat: {message.chat.title}\n**Chatbot has been disabled.**"
        )
        
    else:
        # If no valid command is provided, show a help message
        await message.reply_text(
            "Usage:\n/chatbot on - to enable the chatbot\n/chatbot off - to disable the chatbot"
        )





# Helper function to check unwanted messages (messages starting with special characters)
def is_unwanted_message(message: Message) -> bool:
    return message.text.startswith(("!", "/", "?", "@", "#"))

# Helper function to handle chatbot responses (reply with text or sticker)
async def handle_chatbot_response(client: Client, message: Message, word: str):
    try:
        # Check if the chatbot is enabled for the chat
        chat_status = status_db.find_one({"chat_id": message.chat.id})
        if chat_status and chat_status.get("status") == "disabled":
            # If the chatbot is disabled, do not respond
            return

        # If no reply is present in the message
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

# Handle chat messages for text or stickers in group chats (when the chatbot is enabled)
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
