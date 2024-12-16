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
import openai
from nexichat import nexichat
from nexichat import mongo, db, LOGGER

client = MongoClient(config.MONGO_URL)  # Mongo URI from config
db = client["chatbot_db"]  # Name of your database, can be changed if needed
status_db = db["status"]  # Collection name for storing chatbot status
# OpenAI API key setup
openai.api_key = config.OPENAI  # Set the API key from config


async def get_gpt_response(message_text):
    response = openai.Completion.create(
        model="gpt-3.5-turbo",  # Updated model
        prompt=message_text,
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].text.strip()


# Function to simulate typing each word individually
async def type_message_with_typing(client: Client, chat_id: int, message_text: str):
    """Simulate typing one word at a time."""
    words = message_text.split()  # Split the message into words
    for word in words:
        # Simulate typing action
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(0.5)  # Time delay between words to simulate typing
        # Send the word as a message
        await client.send_message(chat_id, word)
        await asyncio.sleep(1)  # Delay before sending the next word

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
        await message.reply_text(f"Chatbot has been enabled for {message.chat.title}.")
        
    elif command == "off":
        # Disable the chatbot for the chat
        status_db.update_one({"chat_id": chat_id}, {"$set": {"status": "disabled"}}, upsert=True)

        # Send confirmation message
        await message.reply_text(f"Chatbot has been disabled for {message.chat.title}.")
        
    else:
        await message.reply_text(
            "Usage:\n/chatbot on - to enable the chatbot\n/chatbot off - to disable the chatbot"
        )

# Handle chat messages for text in group chats (when the chatbot is enabled)
@nexichat.on_message(filters.text & ~filters.private & ~filters.bot)
async def chatbot_responder(client: Client, message: Message):
    chat_id = message.chat.id

    # Check if the chatbot is enabled
    chatbot_status = status_db.find_one({"chat_id": chat_id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

    # Generate a response using OpenAI GPT
    gpt_response = await get_gpt_response(message.text)
    
    # Send the response with typing effect
    await type_message_with_typing(client, chat_id, gpt_response)

# Chatbot responder for private chats
@nexichat.on_message(filters.text & filters.private & ~filters.bot)
async def chatbot_private(client: Client, message: Message):
    # Check if the chatbot is enabled
    chatbot_status = status_db.find_one({"chat_id": message.chat.id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

    # Generate a response using OpenAI GPT
    gpt_response = await get_gpt_response(message.text)
    
    # Send the response with typing effect
    await type_message_with_typing(client, message.chat.id, gpt_response)
