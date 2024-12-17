import os
import re
import random
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageIdInvalid, ChatAdminRequired, EmoticonInvalid, ReactionInvalid
from random import choice
from pyrogram import Client, filters
from nexichat import nexichat
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from pyrogram.enums import ChatAction
from pymongo import MongoClient

MONGO_DB_URI = "mongodb+srv://teamdaxx123:teamdaxx123@cluster0.ysbpgcp.mongodb.net/?retryWrites=true&w=majority"
# MongoDB Initialization
mongo_client = MongoClient(MONGO_DB_URI)
chatbot_db = mongo_client["VickDb"]["Vick"]  # Stores chatbot status (enabled/disabled)
word_db = mongo_client["Word"]["WordDb"]     # Stores word-response pairs
user_status_db = mongo_client["UserStatus"]["UserDb"]  # Stores user status
locked_words_db = []  # Stores locked words
BOT_OWNER_ID = "7400383704"

# Command to disable the chatbot (works for all users in both private and group chats)
@nexichat.on_message(filters.command(["chatbot off"], prefixes=["/"]))
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
@nexichat.on_message(filters.command(["chatbot on"], prefixes=["/"]))
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
@nexichat.on_message(filters.command(["chatbot"], prefixes=["/"]))
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


# Command to request word lock
@nexichat.on_message(filters.command(["lock"], prefixes=["/"]))
async def lock_word(client, message: Message):
    # Check if the command has a word to lock
    if len(message.text.split()) < 2:
        await message.reply_text("Please provide a word to lock. Example: /lock xxx")
        return

    word_to_lock = message.text.split()[1]
    user_id = message.from_user.id

    # Send a request to the bot owner with inline buttons
    await client.send_message(
        BOT_OWNER_ID,
        f"User {message.from_user.mention(style='md')} has requested to lock the word: **'{word_to_lock}'**.\n\nUser ID: `{user_id}`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Accept", callback_data=f"accept:{word_to_lock}:{user_id}"),
             InlineKeyboardButton("Decline", callback_data=f"decline:{word_to_lock}:{user_id}")]
        ])
    )

    # Notify the user about the request
    await message.reply_text(f"Your request to lock the word '{word_to_lock}' has been sent to the bot owner.")

# Callback handler for buttons
@nexichat.on_callback_query()
async def handle_lock_request(client, callback_query: CallbackQuery):
    try:
        # Extract action, word, and user_id from callback_data
        data = callback_query.data
        if ":" in data:
            action, word_to_lock, user_id = data.split(":")
            user_id = int(user_id)  # Convert user_id to integer

            # Check if the owner clicked the button
            if callback_query.from_user.id == BOT_OWNER_ID:
                if action == "accept":
                    # Add the word to the database
                    locked_words_db.append({"word": word_to_lock})  # Replace with your actual DB logic
                    
                    # Notify owner and user
                    await callback_query.answer(f"Word '{word_to_lock}' has been locked.")
                    await callback_query.message.edit_text(f"The word '{word_to_lock}' has been locked by the owner.")
                    await client.send_message(
                        user_id,
                        f"Your request to lock the word '{word_to_lock}' has been **accepted** by the bot owner."
                    )
                elif action == "decline":
                    # Notify owner and user
                    await callback_query.answer(f"Request to lock the word '{word_to_lock}' has been declined.")
                    await callback_query.message.edit_text(f"The request to lock '{word_to_lock}' has been declined by the owner.")
                    await client.send_message(
                        user_id,
                        f"Your request to lock the word '{word_to_lock}' has been **declined** by the bot owner."
                    )
            else:
                # If the user clicking is not the owner
                await callback_query.answer("You are not authorized to perform this action.", show_alert=True)
        else:
            await callback_query.answer("Invalid callback data.", show_alert=True)
    except Exception as e:
        # Log any errors
        print(f"Error handling callback: {e}")
        await callback_query.answer("An error occurred while processing your request.", show_alert=True)


# Chatbot responder for group chats
@nexichat.on_message((filters.text | filters.sticker) & ~filters.private & ~filters.bot)
async def chatbot_responder(client: Client, message: Message):
    # Filter out unwanted messages
    if re.match(UNWANTED_MESSAGE_REGEX, message.text):
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

    await nexichat.send_chat_action(chat_id, ChatAction.TYPING)

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
@nexichat.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
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

    await nexichat.send_chat_action(message.chat.id, ChatAction.TYPING)

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
