from pyrogram.types import InlineKeyboardButton

from config import SUPPORT_GRP, UPDATE_CHNL
from nexichat import OWNER, nexichat


START_BOT = [
    [
        InlineKeyboardButton(
            text="❖ ᴛᴧᴘ тᴏ sᴇᴇ ᴍᴧɢɪᴄ ❖",
            url="https://t.me/RADHIKA_CHAT_RROBOT?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="˹ ❍ᴡɴᴇꝛ ˼", user_id=OWNER),
        InlineKeyboardButton(text="˹ sᴜᴘᴘᴏꝛᴛ ˼", url=f"https://t.me/{SUPPORT_GRP}"),
    ],
    [
        InlineKeyboardButton(text="˹ ᴜᴘᴅᴀᴛᴇ ˼", url=f"https://t.me/{UPDATE_CHNL}"),
        InlineKeyboardButton(text="˹ ʜᴇʟᴘ ˼", callback_data="HELP"),
    ],
]


PNG_BTN = [
    [
        InlineKeyboardButton(text="↺ ᴄʟᴏsᴇ ↻", callback_data="CLOSE"),
    ],
]


BACK = [
    [
        InlineKeyboardButton(text="↺ ᴄʟᴏsᴇ ↻", callback_data="CLOSE"),
    ],
]


HELP_BTN = [
    [
        InlineKeyboardButton(text="◖ ᴄʜᴀᴛʙᴏᴛ ◗", callback_data="CHATBOT_CMD"),
        InlineKeyboardButton(text="◖ ᴛᴏᴏʟs ◗", callback_data="TOOLS_DATA"),
    ],
    [
        InlineKeyboardButton(text="˹ sᴜᴘᴘᴏʀᴛ ˼", url="https://t.me/+OL6jdTL7JAJjYzVl"),
    ],
    [
        InlineKeyboardButton(text="↺ ʙᴀᴄᴋ ↻", callback_data="HOME_BACK"),
    ],
]


HELP_BTON = [
    [
        InlineKeyboardButton(text="◖ ᴄʜᴀᴛʙᴏᴛ ◗", callback_data="CHATBOT_CMD"),
        InlineKeyboardButton(text="◖ ᴛᴏᴏʟs ◗", callback_data="TOOLS_DATA"),
    ],
    [
        InlineKeyboardButton(text="↺ ᴄʟᴏsᴇ ↻", callback_data="CLOSE"),
    ],
]

CLOSE_BTN = [
    [
        InlineKeyboardButton(text="⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
    ],
]



MUSIC_BACK_BTN = [
    [
        InlineKeyboardButton(text="sᴏᴏɴ", callback_data=f"soom"),
    ],
]

S_BACK = [
    [
        InlineKeyboardButton(text="⦿ ʙᴀᴄᴋ ⦿", callback_data="SBACK"),
        InlineKeyboardButton(text="⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
    ],
]


CHATBOT_BACK = [
    [
        InlineKeyboardButton(text="↺ ʙᴀᴄᴋ ↻", callback_data="CHATBOT_BACK"),
        InlineKeyboardButton(text="↺ ᴄʟᴏsᴇ ↻", callback_data="CLOSE"),
    ],
]


HELP_START = [
    [
        InlineKeyboardButton(text="« ʜᴇʟᴘ »", callback_data="HELP"),
        InlineKeyboardButton(text="🐳 ᴄʟᴏsᴇ 🐳", callback_data="CLOSE"),
    ],
]


HELP_BUTN = [
    [
        InlineKeyboardButton(text="➥ ᴏᴘᴇɴ ɪɴ ᴘʀɪᴠɪᴛᴇ", url="https://t.me/RADHIKA_CHAT_RROBOT?start=help"),
    ],
]
