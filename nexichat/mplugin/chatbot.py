import random
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from pymongo import MongoClient

MONGO_DB_URI = "mongodb+srv://teamdaxx123:teamdaxx123@cluster0.ysbpgcp.mongodb.net/?retryWrites=true&w=majority"
# MongoDB Initialization
mongo_client = MongoClient(MONGO_DB_URI)
chatbot_db = mongo_client["VickDb"]["Vick"]  # Stores chatbot status (enabled/disabled)
word_db = mongo_client["Word"]["WordDb"]     # Stores word-response pairs
user_status_db = mongo_client["UserStatus"]["UserDb"]  # Stores user status

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
        await message.reply_text("Chatbot Disabled in Private Chat!")
    else:
        await message.reply_text("Chatbot Disabled in Group!")

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
        await message.reply_text("Chatbot Enabled in Private Chat!")
    else:
        await message.reply_text("Chatbot Enabled in Group!")

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
        await message.reply_text(f"**Usage:**\n`/chatbot [on/off]`\n{status_message}\nChatbot commands work here!")
    else:
        # Group chat
        await message.reply_text(f"**Usage:**\n`/chatbot [on/off]`\n{status_message}\nChatbot commands only work in groups.")


# Chatbot responder for group chats
@Client.on_message((filters.text | filters.sticker) & ~filters.private & ~filters.bot)
async def chatbot_responder(client: Client, message: Message):
    chat_id = message.chat.id

    # Check if the chatbot is enabled
    chatbot_status = chatbot_db.find_one({"chat_id": chat_id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

    await app.send_chat_action(chat_id, ChatAction.TYPING)

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

# Chatbot responder for private chats
@Client.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
async def chatbot_private(client: Client, message: Message):
    # Check if the chatbot is enabled
    chatbot_status = chatbot_db.find_one({"chat_id": message.chat.id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

    await app.send_chat_action(message.chat.id, ChatAction.TYPING)

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
