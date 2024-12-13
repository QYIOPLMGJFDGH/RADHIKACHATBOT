from config import OWNER_USERNAME, SUPPORT_GRP
from nexichat import nexichat
from pyrogram import Client, filters



START = """```
🐰⃟⃞⍣Rᴀᴅʜɪᴋᴀ❥ Oɴ ᴛᴏᴘ ❥```
➥ ᴍᴜʟᴛɪ-ʟᴀɴɢᴜᴀɢᴇ /lang
➥ ᴇɴᴀʙʟᴇᴅ/ᴅɪꜱᴀʙʟᴇᴅ ʙʏ /chatbot
➥ ᴄʟᴏɴᴇ ʙʏ /clone
╔═════════════════╗
║๏ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ : {}
║๏ ᴛᴏᴛᴀʟ ᴄʜᴀᴛꜱ : {}
║๏ ᴜᴘᴛɪᴍᴇ » {}                         
╚═════════════════╝
"""

HELP_READ = f"""```
Aʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /```
Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.  Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ [sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ](https://t.me/+OL6jdTL7JAJjYzVl)
"""

TOOLS_DATA_READ = f"""```
: ̗̀➛ ʜᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ғᴏʀ ᴛᴏᴏʟꜱ:```
彡 /start - Sᴛᴀʀᴛ ʙᴏᴛ !
──────────────
彡 /help - Gᴇᴛ ʜᴇʟᴘ ᴍᴇɴᴜ !
──────────────
彡 /ping - Pɪɴɢ ᴘᴏɴɢ!
──────────────
彡 /broadcast [-user -pin] -  ᴛᴏ ғᴏʀᴡᴀʀᴅ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀʟʟ ᴄʜᴀᴛs !
──────────────
"""

CHATBOT_READ = f"""```
: ̗̀➛ ʜᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅs ғᴏʀ ᴄʜᴀᴛʙᴏᴛ:```
彡 /chatbot - Eɴᴀʙʟᴇ ᴏʀ ᴅɪsᴀʙʟᴇ ᴛʜᴇ ᴄʜᴀᴛʙᴏᴛ.
──────────────
彡 /lang, /language, /setlang - Oᴘᴇɴs ʟᴀɴɢᴜᴀɢᴇ.  
──────────────
彡 /resetlang, /nolang - Rᴇsᴇᴛs ᴛʜᴇ ʙᴏᴛ's ʟᴀɴɢᴜᴀɢᴇ.
──────────────
彡 /status - Cʜᴇᴄᴋ ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs.
──────────────
彡 /stats - Gᴇᴛ ʙᴏᴛ ꜱᴛᴀᴛꜱ.
──────────────
"""

ADMIN_READ = f"sᴏᴏɴ"

ABOUT_RED = f"""
**➻ [jv](https://t.me/Goodbyenjbot) ɪs ᴀɴ ᴀɪ ʙᴀsᴇᴅ ᴄʜᴀᴛ-ʙᴏᴛ.**
**➻ [{nexichat.name}](https://t.me/Goodbyenjbot) ʀᴇᴘʟɪᴇs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴛᴏ ᴀ ᴜsᴇʀ.**
**➻ ʜᴇʟᴘs ʏᴏᴜ ɪɴ ᴀᴄᴛɪᴠᴀᴛɪɴɢ ʏᴏᴜʀ ɢʀᴏᴜᴘs.**
**➻ ᴡʀɪᴛᴛᴇɴ ɪɴ [ᴘʏᴛʜᴏɴ](https://www.python.org) ᴡɪᴛʜ [ᴍᴏɴɢᴏ-ᴅʙ](https://www.mongodb.com) ᴀs ᴀ ᴅᴀᴛᴀʙᴀsᴇ**
**──────────────**
**➻ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ғᴏʀ ɢᴇᴛᴛɪɴɢ ʙᴀsɪᴄ ʜᴇʟᴩ ᴀɴᴅ ɪɴғᴏ ᴀʙᴏᴜᴛ [you](https://t.me/Goodbyenjbot)**
"""
