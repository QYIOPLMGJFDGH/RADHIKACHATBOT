import os
import re
import random
from config import MONGO_URL
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageIdInvalid, ChatAdminRequired, EmoticonInvalid, ReactionInvalid
from pyrogram import Client, filters
from nexichat import CLONE_OWNERS
from nexichat.mplugin.Callback import cb_handler
from pyrogram.types import CallbackQuery
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ChatAction
from pymongo import MongoClient

# MongoDB Initialization
mongo_client = MongoClient(MONGO_URL)
chatbot_db = mongo_client["VickDb"]["Vick"]  # Stores chatbot status (enabled/disabled)
word_db = mongo_client["Word"]["WordDb"]     # Stores word-response pairs
user_status_db = mongo_client["UserStatus"]["UserDb"]  # Stores user status
locked_words_db = mongo_client["LockedWords"]["LockedWordsDb"]
BOT_OWNER_ID = 7400383704

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

# Regular expression to filter unwanted messages containing special characters like /, !, ?, ~, \
UNWANTED_MESSAGE_REGEX = r"^[\W_]+$|[\/!?\~\\]"

# Function to check if the user is the bot owner
async def is_owner(client, user_id):
    bot_id = (await client.get_me()).id
    return user_id == BOT_OWNER_ID  # Use the bot owner's ID here

# Command to lock a word (Owner Only)
@Client.on_message(filters.command("lock", prefixes=["/"]))
async def lock_word(client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("Please provide a word to lock. Example: /lock <word>")
        return

    word_to_lock = message.text.split()[1]
    user_id = message.from_user.id

    # Check if the user is the owner
    if await is_owner(client, user_id):
        await message.reply_text(f"You are the owner. The word '{word_to_lock}' is now locked.")
        locked_words_db.insert_one({"word": word_to_lock})
    else:
        # Notify user that only the owner can lock words
        await message.reply_text("Only the owner can lock words.")

# Command to delete a locked word (Owner Only)
@Client.on_message(filters.command("del", prefixes=["/"]) & filters.user(BOT_OWNER_ID))
async def delete_locked_word(client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("Please specify a word to delete. Example: `/del <word>`")
        return

    word_to_delete = message.text.split()[1]
    deleted_word = locked_words_db.find_one_and_delete({"word": word_to_delete})

    if deleted_word:
        await message.reply_text(f"The word '{word_to_delete}' has been successfully deleted.")
    else:
        await message.reply_text(f"The word '{word_to_delete}' was not found in the locked words list.")

# Command to request word lock
@Client.on_message(filters.command("lock", prefixes=["/"]))
async def request_lock_word(client, message: Message):
    if len(message.text.split()) < 2:
        await message.reply_text("Please provide a word to lock. Example: /lock <word>")
        return

    word_to_lock = message.text.split()[1]
    user_id = message.from_user.id

    # Send a request to the owner
    await nexichat.send_message(
        BOT_OWNER_ID,
        f"User {message.from_user.mention(style='md')} has requested to lock the word: **'{word_to_lock}'**.\n\nUser ID: `{user_id}`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Accept", callback_data=f"accept:{word_to_lock}:{user_id}"),
             InlineKeyboardButton("Decline", callback_data=f"decline:{word_to_lock}:{user_id}")]
        ])
    )
    await message.reply_text(f"Your request to lock the word '{word_to_lock}' has been sent to the bot owner.")

# Callback handler for Accept/Decline actions
@Client.on_callback_query()
async def cb_handler(client: Client, callback_query: CallbackQuery):
    action, word_to_lock, user_id = callback_query.data.split(":")
    user_id = int(user_id)

    if action == "accept":
        locked_words_db.insert_one({"word": word_to_lock})
        await callback_query.answer(f"The word '{word_to_lock}' has been locked.")
    elif action == "decline":
        await callback_query.answer(f"The request to lock the word '{word_to_lock}' has been declined.")

# Chatbot responder for group chats
@Client.on_message((filters.text | filters.sticker) & ~filters.private & ~filters.bot)
async def chatbot_responder(client: Client, message: Message):
    # Ensure message.text is not None before using re.match
    if message.text and re.match(UNWANTED_MESSAGE_REGEX, message.text):
        return

    chat_id = message.chat.id

    # Check if the chatbot is enabled
    chatbot_status = chatbot_db.find_one({"chat_id": chat_id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

    # Check if the word is locked
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

# Chatbot responder for private chats
@Client.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
async def chatbot_private(client: Client, message: Message):
    # Filter out unwanted messages
    if re.match(UNWANTED_MESSAGE_REGEX, message.text):
        return

    # Check if the chatbot is enabled
    chatbot_status = chatbot_db.find_one({"chat_id": message.chat.id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

    # Check if the word is locked
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
