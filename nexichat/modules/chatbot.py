import random
import asyncio
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.types import CallbackQuery
from pyrogram.enums import ChatMemberStatus as CMS
import config
from nexichat import nexichat
from nexichat import mongo, db, LOGGER

# MongoDB connection setup
client_db = MongoClient(config.MONGO_URL)
chatai = client_db["Word"]["WordDb"]
vick_db = client_db["VickDb"]["Vick"]
status_db = client_db["StatusDb"]["ChatStatus"]  # Chat status collection
word_db = client_db["WordDb"]["Words"]  # Database to store word responses

# Handle the /chatbot command to enable or disable the chatbot
@nexichat.on_message(filters.command("chatbot"))
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
            f"Cʜᴀᴛ: ➥ {message.chat.title}\nCʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ ᴇɴᴀʙʟᴇᴅ."
        )
        
    elif command == "off":
        # Disable the chatbot for the chat
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "disabled"}}, upsert=True)

        # Send confirmation message
        await message.reply_text(
            f"Cʜᴀᴛ: ➥{message.chat.title}\nCʜᴀᴛʙᴏᴛ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ."
        )
        
    else:
        # If no valid command is provided, show a help message
        await message.reply_text(
            "Usᴇs:⤸⤸⤸\n/chatbot on - ᴛᴏ ᴇɴᴀʙʟᴇ ᴛʜᴇ ᴄʜᴀᴛʙᴏᴛ\n/chatbot off - ᴛᴏ ᴅɪsᴀʙʟᴇ ᴛʜᴇ ᴄʜᴀᴛʙᴏᴛ"
        )

# Handle /status command to check the chatbot status in private chats
@nexichat.on_message(filters.command("status") & (filters.private | filters.group))
async def status_command(client: Client, message: Message):
    """Handle /status command to show chatbot status in private chat and group chat."""
    chat_id = message.chat.id
    chat_status = status_db.find_one({"chat_id": chat_id})

    if chat_status and chat_status.get("status") == "enabled":
        status_message = "ᴄʜᴀᴛʙᴏᴛ : ᴇɴᴀʙʟᴇᴅ"
    else:
        status_message = "ᴄʜᴀᴛʙᴏᴛ : ᴅɪsᴀʙʟᴇᴅ"

    # If the message is in a group, reply in the group, otherwise in private
    if message.chat.type == "private":
        await message.reply_text(status_message)
    else:
        await message.reply_text(f"{status_message}")

# Helper function to check unwanted messages
def is_unwanted_message(message: Message) -> bool:
    return message.text.startswith(("!", "/", "?", "@", "#"))

# Handle chat messages for text or stickers in group chats (when the chatbot is enabled)
@nexichat.on_message((filters.text | filters.sticker) & ~filters.private & ~filters.bot)
async def chatbot_responder(client: Client, message: Message):
    chat_id = message.chat.id

    # Check if the chatbot is enabled
    chatbot_status = status_db.find_one({"chat_id": chat_id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

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
        if reply.from_user.id == (await client.get_me()).id:
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

# Chatbot responder for private chats
@nexichat.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
async def chatbot_private(client: Client, message: Message):
    # Check if the chatbot is enabled
    chatbot_status = status_db.find_one({"chat_id": message.chat.id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

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
        if reply.from_user.id == (await client.get_me()).id:
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
