import random
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.errors import MessageEmpty
from pyrogram.enums import ChatAction
from datetime import datetime, timedelta
from pyrogram.types import Message
from deep_translator import GoogleTranslator 
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from config import MONGO_URL
from nexichat import mongo, db
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup
import asyncio
import config
from nexichat import LOGGER
from nexichat import nexichat as shizuchat

translator = GoogleTranslator()  

lang_db = db.ChatLangDb.LangCollection
status_db = db.chatbot_status_db.status

replies_cache = []
new_replies_cache = []

blocklist = {}
message_counts = {}
translation_cache = {}  # Cache for translated text

# Efficient Cache Loader (Only reload if necessary)
async def reload_cache():
    global replies_cache
    try:
        replies_cache = await chatai.find().to_list(length=None)
    except Exception as e:
        print(f"Error in reload_cache: {e}")

# Optimized chat language fetching (cache the results)
async def get_chat_language(chat_id):
    if chat_id not in lang_cache:
        chat_lang = await lang_db.find_one({"chat_id": chat_id})
        lang_cache[chat_id] = chat_lang["language"] if chat_lang and "language" in chat_lang else "en"
    return lang_cache.get(chat_id, "en")

# Optimized Spam Detection (Check every 5 messages instead of 4)
async def check_spam(user_id, current_time):
    global message_counts
    if user_id not in message_counts:
        message_counts[user_id] = {"count": 1, "last_time": current_time}
    else:
        time_diff = (current_time - message_counts[user_id]["last_time"]).total_seconds()
        if time_diff <= 3:  # 3 seconds interval check
            message_counts[user_id]["count"] += 1
        else:
            message_counts[user_id] = {"count": 1, "last_time": current_time}
        
        if message_counts[user_id]["count"] >= 5:  # Increased message count threshold
            blocklist[user_id] = current_time + timedelta(minutes=1)
            message_counts.pop(user_id, None)
            return True
    return False

async def chatbot_response(client: Client, message: Message):
    global blocklist, message_counts
    try:
        user_id = message.from_user.id
        chat_id = message.chat.id
        current_time = datetime.now()
        
        blocklist = {uid: time for uid, time in blocklist.items() if time > current_time}

        if user_id in blocklist:
            return

        if await check_spam(user_id, current_time):
            await message.reply_text(f"**Hey, {message.from_user.mention}**\n\n**You are blocked for 1 minute due to spam messages.**\n**Try again after 1 minute 🤣.**")
            return

        chat_status = await status_db.find_one({"chat_id": chat_id})
        if chat_status and chat_status.get("status") == "disabled":
            return

        if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            if message.chat.type == "group" or message.chat.type == "supergroup":
                return await add_served_chat(message.chat.id)
            else:
                return await add_served_user(message.chat.id)
        
        if (message.reply_to_message and message.reply_to_message.from_user.id == shizuchat.id) or not message.reply_to_message:
            reply_data = await get_reply(message.text)

            if reply_data:
                response_text = reply_data["text"]
                chat_lang = await get_chat_language(chat_id)

                # Check if translation exists in the cache
                if chat_lang not in translation_cache:
                    translation_cache[chat_lang] = {}

                if message.text not in translation_cache[chat_lang]:
                    if chat_lang == "en":
                        translated_text = response_text
                    else:
                        translated_text = GoogleTranslator(source='auto', target=chat_lang).translate(response_text)
                    translation_cache[chat_lang][message.text] = translated_text
                else:
                    translated_text = translation_cache[chat_lang][message.text]
                
                if reply_data["check"] == "sticker":
                    await message.reply_sticker(reply_data["text"])
                elif reply_data["check"] == "photo":
                    await message.reply_photo(reply_data["text"])
                elif reply_data["check"] == "video":
                    await message.reply_video(reply_data["text"])
                elif reply_data["check"] == "audio":
                    await message.reply_audio(reply_data["text"])
                elif reply_data["check"] == "voice":
                    await message.reply_voice(reply_data["text"])
                elif reply_data["check"] == "gif":
                    await message.reply_animation(reply_data["text"]) 
                else:
                    await message.reply_text(translated_text)
                    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            else:
                await message.reply_text("**I don't understand. What are you saying??**")
        
        if message.reply_to_message:
            await save_reply(message.reply_to_message, message)
    except MessageEmpty as e:
        return await message.reply_text("🙄🙄")
    except Exception as e:
        print(f"Error: {e}")
        return

# Optimized Reply Retrieval (Cache for replies)
async def get_reply(word: str):
    try:
        is_chat = [reply for reply in replies_cache if reply.get("word") == word]
        
        if not is_chat:
            await reload_cache()
            is_chat = [reply for reply in replies_cache if reply.get("word") == word]

        if not is_chat:
            return random.choice(replies_cache) if replies_cache else None
        
        return random.choice(is_chat)
    except Exception as e:
        print(f"Error in get_reply: {e}")
        return None

# Save New Reply (Save replies only if new)
async def save_reply(original_message: Message, reply_message: Message):
    try:
        new_reply = None

        if reply_message.sticker:
            new_reply = {
                "word": original_message.text,
                "text": reply_message.sticker.file_id,
                "check": "sticker",
            }
        elif reply_message.photo:
            new_reply = {
                "word": original_message.text,
                "text": reply_message.photo.file_id,
                "check": "photo",
            }
        elif reply_message.video:
            new_reply = {
                "word": original_message.text,
                "text": reply_message.video.file_id,
                "check": "video",
            }
        elif reply_message.audio:
            new_reply = {
                "word": original_message.text,
                "text": reply_message.audio.file_id,
                "check": "audio",
            }
        elif reply_message.voice:
            new_reply = {
                "word": original_message.text,
                "text": reply_message.voice.file_id,
                "check": "voice",
            }
        elif reply_message.animation:
            new_reply = {
                "word": original_message.text,
                "text": reply_message.animation.file_id,
                "check": "gif",
            }
        elif reply_message.text:
            translated_text = reply_message.text
            try:
                translated_text = GoogleTranslator(source='auto', target='en').translate(reply_message.text)
            except Exception as e:
                print(f"Translation error: {e}, saving original text.")
                translated_text = reply_message.text

            new_reply = {
                "word": original_message.text,
                "text": translated_text,
                "check": "none",
            }

        if new_reply:
            is_chat = await chatai.find_one(new_reply)
            if not is_chat:
                await chatai.insert_one(new_reply)
                replies_cache.append(new_reply)
                print(f"Replies saved: {original_message.text} == {reply_message.text}")
            else:
                print(f"Replies found: {original_message.text} == {reply_message.text}")

    except Exception as e:
        print(f"Error in save_reply: {e}")

