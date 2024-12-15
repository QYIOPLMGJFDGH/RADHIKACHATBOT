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

# MongoDB connection setup for 5 different MongoDBs
client_db_1 = MongoClient(config.MONGO_URL_1)
client_db_2 = MongoClient(config.MONGO_URL_2)
client_db_3 = MongoClient(config.MONGO_URL_3)
client_db_4 = MongoClient(config.MONGO_URL_4)
client_db_5 = MongoClient(config.MONGO_URL_5)

# Defining collections for each MongoDB
db1_chats = client_db_1["ChatsDb"]["ChatCollection1"]
db2_chats = client_db_2["ChatsDb"]["ChatCollection2"]
db3_chats = client_db_3["ChatsDb"]["ChatCollection3"]
db4_chats = client_db_4["ChatsDb"]["ChatCollection4"]
db5_chats = client_db_5["ChatsDb"]["ChatCollection5"]

# Status DB (for enabling/disabling chatbot)
status_db = client_db_1["StatusDb"]["ChatStatus"]

# Helper function to store chat data into 5 databases
def store_in_databases(chat_id, user_id, message, date):
    db1_chats.insert_one({"chat_id": chat_id, "user_id": user_id, "message": message, "date": date})
    db2_chats.insert_one({"chat_id": chat_id, "user_id": user_id, "message": message, "date": date})
    db3_chats.insert_one({"chat_id": chat_id, "user_id": user_id, "message": message, "date": date})
    db4_chats.insert_one({"chat_id": chat_id, "user_id": user_id, "message": message, "date": date})
    db5_chats.insert_one({"chat_id": chat_id, "user_id": user_id, "message": message, "date": date})

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

    # Store the chat message in the 5 databases for historical tracking
    store_in_databases(chat_id, message.from_user.id, message.text, message.date)

    # Check if it's a reply
    if not message.reply_to_message:
        responses = []
        # Query from multiple databases
        for db in [db1_chats, db2_chats, db3_chats, db4_chats, db5_chats]:
            responses.extend(list(db.find({"message": {"$regex": f'.*{message.text}.*', "$options": 'i'}})))
        
        # Filter and select unique responses
        unique_responses = list(set([response["message"] for response in responses]))
        if unique_responses:
            # Choose a random response for uniqueness
            response = random.choice(unique_responses)
            # Call the typing effect function to type each word
            await type_message_with_typing(client, chat_id, response)
    else:
        reply = message.reply_to_message
        if reply.from_user.id == (await client.get_me()).id:
            responses = []
            for db in [db1_chats, db2_chats, db3_chats, db4_chats, db5_chats]:
                responses.extend(list(db.find({"message": {"$regex": f'.*{message.text}.*', "$options": 'i'}})))
            
            unique_responses = list(set([response["message"] for response in responses]))
            if unique_responses:
                response = random.choice(unique_responses)
                await type_message_with_typing(client, chat_id, response)
        else:
            # Store the message if it's a reply from another user
            store_in_databases(chat_id, message.from_user.id, message.text, message.date)

# Chatbot responder for private chats
@nexichat.on_message((filters.text | filters.sticker) & filters.private & ~filters.bot)
async def chatbot_private(client: Client, message: Message):
    # Check if the chatbot is enabled
    chatbot_status = status_db.find_one({"chat_id": message.chat.id})
    if not chatbot_status or chatbot_status.get("status") == "disabled":
        return

    # Store the chat message in the 5 databases for historical tracking
    store_in_databases(message.chat.id, message.from_user.id, message.text, message.date)

    if not message.reply_to_message:
        responses = []
        for db in [db1_chats, db2_chats, db3_chats, db4_chats, db5_chats]:
            responses.extend(list(db.find({"message": {"$regex": f'.*{message.text}.*', "$options": 'i'}})))
        
        unique_responses = list(set([response["message"] for response in responses]))
        if unique_responses:
            response = random.choice(unique_responses)
            await type_message_with_typing(client, message.chat.id, response)
    else:
        reply = message.reply_to_message
        if reply.from_user.id == (await client.get_me()).id:
            responses = []
            for db in [db1_chats, db2_chats, db3_chats, db4_chats, db5_chats]:
                responses.extend(list(db.find({"message": {"$regex": f'.*{message.text}.*', "$options": 'i'}})))
            
            unique_responses = list(set([response["message"] for response in responses]))
            if unique_responses:
                response = random.choice(unique_responses)
                await type_message_with_typing(client, message.chat.id, response)
        else:
            if message.text:
                store_in_databases(message.chat.id, message.from_user.id, message.text, message.date)
