import random
import asyncio
from pymongo import MongoClient
from pyrogram import filters
from pyrogram import Client
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
from pyrogram.enums import ChatMemberStatus as CMS
import config
from nexichat import mongo, db, LOGGER

# MongoDB connection setup
client_db = MongoClient(config.MONGO_URL)
chatai = client_db["Word"]["WordDb"]
vick_db = client_db["VickDb"]["Vick"]
status_db = client_db["StatusDb"]["ChatStatus"]  # Chat status collection

# Handle the /chatbot command to enable or disable the chatbot
@Client.on_message(filters.command("chatbot"))
async def chatbot_command(client: Client, message: Message):
    """Handle /chatbot command to enable/disable chatbot."""
    if len(message.command) > 1:
        command = message.command[1].lower()  # Get the second part of the command
    else:
        command = ''

    chat_id = message.chat.id
    if command == "on":
        # Enable the chatbot for the chat
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "enabled"}}, upsert=True)
        
        # Send confirmation message
        await message.reply_text(
            f"Cʜᴀᴛ: ➥ {message.chat.title}\nCʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ.**"
        )
        
    elif command == "off":
        # Disable the chatbot for the chat
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "disabled"}}, upsert=True)

        # Send confirmation message
        await message.reply_text(
            f"Cʜᴀᴛ: ➥{message.chat.title}\n**Cʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.**"
        )
        
    else:
        # If no valid command is provided, show a help message
        await message.reply_text(
            "Usᴇs:⤸⤸⤸\n/chatbot on - ᴛᴏ ᴇɴᴀʙʟᴇ ᴛʜᴇ ᴄʜᴀᴛʙᴏᴛ\n/chatbot off - ᴛᴏ ᴅɪsᴀʙʟᴇ ᴛʜᴇ ᴄʜᴀᴛʙᴏᴛ"
        )

# Handle /status command to check the chatbot status in private chats
@Client.on_message(filters.command("status") & filters.private)
async def status_command(client: Client, message: Message):
    """Handle /status command to show chatbot status in private chat."""
    user_id = message.from_user.id
    chat_status = status_db.find_one({"chat_id": user_id})

    if chat_status and chat_status.get("status") == "enabled":
        await message.reply_text("ᴄʜᴀᴛʙᴏᴛ : ᴇɴᴀʙʟᴇ")
    else:
        await message.reply_text("ᴄʜᴀᴛʙᴏᴛ : ᴅɪsᴀʙʟᴇ")

# Helper function to check unwanted messages
def is_unwanted_message(message: Message) -> bool:
    return message.text.startswith(("!", "/", "?", "@", "#"))

# Handle chat messages for text or stickers in group chats (when the chatbot is enabled)
@Client.on_message((filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot)
async def chatbot_response(client: Client, message: Message):
    try:
        if is_unwanted_message(message):
            return
        
        # Check if the chatbot is enabled for the group
        chat_status = status_db.find_one({"chat_id": message.chat.id})
        if chat_status and chat_status.get("status") == "disabled":
            # If the chatbot is disabled, do not respond
            return

        word = message.text if message.text else message.sticker.file_unique_id
        await handle_chatbot_response(client, message, word)
    except Exception as e:
        LOGGER.error(f"Error in chatbot_response: {e}")

# Private chat response (handling private messages)
@Client.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
async def vickprivate(client: Client, message: Message):
    try:
        # Check if the chatbot is enabled for the user
        user_status = status_db.find_one({"chat_id": message.from_user.id})
        if user_status and user_status.get("status") == "disabled":
            return

        word = message.text if message.text else message.sticker.file_unique_id
        await handle_chatbot_response(client, message, word)
    except Exception as e:
        LOGGER.error(f"Error in vickprivate: {e}")

# Helper function to handle chatbot responses (reply with text or sticker)
async def handle_chatbot_response(client: Client, message: Message, word: str):
    try:
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
