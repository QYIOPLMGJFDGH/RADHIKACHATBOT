from config import OWNER_USERNAME, SUPPORT_GRP
from nexichat import nexichat
from pyrogram import Client, filters



START = """<pre>🐰⃟⃞⍣Rᴀᴅʜɪᴋᴀ❥ Cʟᴏɴᴇᦔ Bᴏᴛ ❥</pre>
<pre><code class="language-➥ ᴇɴᴀʙʟᴇᴅ/ᴅɪꜱᴀʙʟᴇᴅ ʙʏ /chatbot">➥ ᴄʟᴏɴᴇ ʙʏ /clone</code></pre>
<blockquote expandable>╔═════════════════╗
║⥂ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ ⬀ {}
║⥂ ᴛᴏᴛᴀʟ ᴄʜᴀᴛꜱ ⬀ {}
║⥂ ᴜᴘᴛɪᴍᴇ ⬀ {}               
╚═════════════════╝</blockquote>
"""


HELP_READ = f"""```
Aʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ: /```
Cʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ғᴏʀ ᴍᴏʀᴇ ɪɴғᴏʀᴍᴀᴛɪᴏɴ.  Iғ ʏᴏᴜ'ʀᴇ ғᴀᴄɪɴɢ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ ʏᴏᴜ ᴄᴀɴ ᴀsᴋ ɪɴ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ
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
彡 /status - Cʜᴇᴄᴋ ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs.
──────────────
彡 /stats - Gᴇᴛ ʙᴏᴛ ꜱᴛᴀᴛꜱ.
──────────────
"""

ADMIN_READ = f"sᴏᴏɴ"
