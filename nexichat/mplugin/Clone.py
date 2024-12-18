import logging
import os
from pyrogram.enums import ParseMode
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
import config
from nexichat.mplugin.helpers import is_owner
from config import API_HASH, API_ID, OWNER_ID
from nexichat import CLONE_OWNERS
from nexichat import nexichat as app
from nexichat import db as mongodb

CLONES = set()
cloneownerdb = mongodb.cloneownerdb
clonebotdb = mongodb.clonebotdb

async def save_clonebot_owner(bot_id, user_id):
    await cloneownerdb.insert_one({"bot_id": bot_id, "user_id": user_id})

@Client.on_message(filters.command(["clone", "host", "deploy"]))
async def clone_txt(client, message):
    # If no bot token is provided after the command
    if len(message.command) <= 1:
        await message.reply_text(f"**Gᴏ ᴛᴏ ᴛʜᴇ ᴍᴀɪɴ ʙᴏᴛ @RADHIKA_CHAT_RROBOT ᴛᴏ ᴄʟᴏɴᴇ ʏᴏᴜʀ ʙᴏᴛ.**")
        return

    # No need to handle the bot token and cloning process here
    await message.reply_text("**Cʟᴏɴɪɴɢ ғᴜᴛᴜʀᴇs ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴜɴᴀᴠᴀɪʟᴀʙʟᴇ ʜᴇʀᴇ. Pʟᴇᴀsᴇ vɪsɪᴛ @RADHIKA_CHAT_RROBOT ᴛᴏ ᴄʟᴏɴᴇ ʏᴏᴜʀ ʙᴏᴛ.**")
