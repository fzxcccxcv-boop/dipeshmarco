# ════════════════════════════════════════════════════════════════════════════
#   DIPESHXMARCO ULTIMATE HOSTER BOT + USERBOT ENGINE + DYNAMIC WEB SERVER
# ════════════════════════════════════════════════════════════════════════════

import asyncio
import logging
import os
import sys
import time
import shutil
import random
import json
import threading
from io import BytesIO
from datetime import datetime
from collections import defaultdict, deque
from pathlib import Path

from flask import Flask, request, jsonify, render_template

# --- Gtts Import ---
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ParseMode

from telethon import TelegramClient, events, utils
from telethon.sessions import StringSession
from telethon.errors import (
    SessionPasswordNeededError, PhoneCodeExpiredError,
    PhoneCodeInvalidError, FloodWaitError
)
from telethon.tl.functions.channels import EditAdminRequest, EditBannedRequest, EditTitleRequest
from telethon.tl.functions.messages import DeleteMessagesRequest, CreateChatRequest, EditChatTitleRequest
from telethon.tl.types import ChatAdminRights, ChatBannedRights

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

START_TIME = time.time()

# ─── BOT & WEB CONFIGURATION ──────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8629618999:AAG4CtSRQDZzr_bqPc5cDSiRn54JzwxoOGM")
OWNER_ID = int(os.environ.get("OWNER_ID", 8115054010))
TELEGRAM_API_ID = int(os.environ.get("TELEGRAM_API_ID", 38843772))
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "875fbb273801c8025d05e98173fca536")
SUPPORT_USERNAME = os.environ.get("SUPPORT_USERNAME", "@DipeshxmarcoSupport")
WEB_ADMIN_KEY = os.environ.get("WEB_ADMIN_KEY", "dipeshxmarco")
PORT = int(os.environ.get("PORT", 8080))
MAX_ACCOUNTS_PER_USER = 3
MAX_USERBOTS = 50

# ─── CONVERSATION STATES ──────────────────────────────────────────────────────
ASK_PHONE, ASK_CODE, ASK_2FA = range(3)
pending_logins: dict = {}
web_pending_logins: dict = {}

# ─── DEFAULT BUILT-IN TEXT BANKS (DIPESH / MARCO / DIPESHXMARCO) ──────────────
DEFAULT_TEXT_BANKS = {
    "RAID_TEXTS": [
        "🔥 DIPESHXMARCO IS HERE TO DOMINATE! BOW DOWN! 🔥",
        "💀 YOUR CHAT BELONGS TO DIPESH NOW! 💀",
        "⚡ FEEL THE POWER OF MARCO'S ULTIMATE BOT! ⚡",
        "🗑️ THIS CHAT IS TRASH, DIPESHXMARCO IS CLEANING IT UP! 🗑️",
        "💥 DIPESH ULTIMATE STRIKES AGAIN! 💥",
        "👑 MARCO IS THE KING HERE! RESPECT THE NAME! 👑",
        "🌪️ A TSUNAMI OF SPAM BY DIPESHXMARCO! 🌪️",
        "🩸 NO MERCY FROM DIPESH & MARCO! 🩸",
        "🚫 ALL YOUR EFFORTS ARE USELESS AGAINST DIPESH! 🚫",
        "💣 PREPARE FOR TOTAL DESTRUCTION! MARCO IS IN CONTROL! 💣"
    ],
    "GAALI_LIST": [
        "⚡ Dipesh ke saamne bolne ki aukaat mat rakh warna pura group lock kar dunga! 😡🔥",
        "💀 Marco ka engine chalu ho gaya hai, ab bhaagne ka rasta dhund! 🚀",
        "🔥 Dipeshxmarco se panga mat le warna chat history saaf ho jayegi! 👑",
        "⚔️ Dipesh ki speed ke aage tera keyboard hang ho jayega beta! 💥",
        "🌪️ Marco ne entry maar li hai, ab sab kone mein baitho! 😎⚡",
        "👑 Asli boss Dipesh hai, baaki sab copy-paste wale bache hain! 🔥",
        "💣 Marco ka blaster chalega toh server hil jayega! 💀",
        "🚀 Dipeshxmarco empire rules this territory! 🏴‍☠️",
        "⚡ Dipesh ke ek command pe poora lobby khali! 🧹🔥",
        "🗡️ Marco ke aage koi tik nahi sakta, seedha surrender kar de! 👑",
        "डालते ही झड़ गए सब, टिका न कोई भी फूल गले में Dipesh के हार के !",
        "Marco से पंगा लिया तो याद रखेगा पूरा टेलीग्राम ज़माना ! 🔥"
    ],
    "reply_texts": [
        "𝐊ʏᴀ 𝐑ᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐉ʜᴜᴋ 𝐀ᴘɴᴇ 𝐁ᴏss 𝐃ɪᴘᴇ𝐬𝐡 𝐊ᴇ 𝐒ᴀᴀᴍɴᴇ - 🦢💘",
        "𝐒ᴀʙᴋɪ 𝐁ᴏʟᴛɪ 𝐁ᴀɴᴅ 𝐇ᴏ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ 𝐌𝐚𝐫𝐜𝐨 ! 🌙",
        "acha beta 😂🔥👊🏻 ? koi na me toh Dipeshxmarco fan hu HATER pelunga 😹💔🔥😆👊🏻💥",
        "Dipesh ko dekh ke bhaga kaise 😂💥🤣🤘🏻",
        "ne toh 𝐌𝐚𝐫𝐜ᴏ ka khauf maan liya 😂🙏🏻😂🙏🏻",
        "Dipesh सूर्य☀ nikalte hi lobby pel de 😹🔥💔",
        "Marco ke samne aawaz niche 😂✊🏻💦",
        "𝐓ᴇʀᴇ 𝐆𝐂 pe 𝐃ɪᴘᴇ𝐬𝐡𝐱𝐦𝐚𝐫𝐜𝐨 ka hamla 😂⚔🔥💥",
        "𝐂ʜᴀʟ 𝐍ɪᴋᴀʟ 𝐃ɪᴘᴇ𝐬𝐡 𝐊ᴇ 𝐒ᴀᴀᴍɴᴇ 𝐒ᴇ 💛🤍🩵",
        "oi 𝐌𝐚𝐫𝐜ᴏ का गुलाम ₰🖤",
        "chl beta Dipeshxmarco se bhid ke dikha 😂💥🤣🔥",
        "𝐌𝐚𝐫𝐜ᴏ 𝐀𝐚 𝐆𝐚𝐲𝐚 naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
        "tera baap bass 𝐃ɪᴘᴇ𝐬𝐡 hai 😂🎀",
        "Marco ke aate hi sab gayab -#😹🔥🥀",
        "𝐏ᴜʀᴀ 𝐒ʏsᴛᴇᴍ 𝐇ɪʟᴀ 𝐃ɪʏᴀ 𝐃ɪᴘᴇ𝐬𝐡𝐱𝐦𝐚𝐫𝐜𝐨 𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜"
    ],
    "fun_texts": [
        "𓂃☁︎ 𓂃𝐒ɪᴅᴇ 𝐇ᴀᴛ 𝐆ᴜʟᴀᴍ 𝐃ɪᴘᴇ𝐬𝐡 𝐊ɪ 𝐒ᴜᴘᴇʀफास्ट रेलगाड़ी आ रही .-'🚂-'.ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
        "⋆⭒˚.⋆🔭 𝐒ʜᴜᴛ 𝐔ᴘ 𝐁ᴇᴛᴀ 𝐌𝐚𝐫𝐜𝐨 𝐊ᴀ 𝐃ᴏᴍɪɴᴀᴛɪᴏɴ 𝐄ɴᴊᴏʏ 𝐊ʀ 𝐓ᴇʟᴇ𝐒ᴄᴏᴘᴇ 𝐒ᴇ⋆⭒˚.⋆🔭",
        "⚡ 𝐃ɪᴘᴇ𝐬𝐡𝐱𝐦𝐚𝐫𝐜𝐨 𝐔ʟᴛɪᴍᴀᴛᴇ 𝐕ɪᴘ 𝐄ɴɢɪɴᴇ 𝐋ᴏᴀᴅᴇᴅ 𝟏𝟎𝟎% 🚀✨",
        "👑 𝐃ɪᴘᴇ𝐬𝐡 & 𝐌𝐚𝐫𝐜𝐨 𝐔ɴsᴛᴏᴘᴘᴀʙʟᴇ 𝐃ᴜᴏ 🔥💥"
    ],
    "flag_texts": [
        " ོ༘₊⁺🇮🇳 ₊⁺⋆.˚ 𝐓ᴇʀᴇ 𝐆𝐂 𝐌ᴇɪɴ 𝐃ɪᴘᴇ𝐬𝐡 𝐁ᴏss 𝐀ᴜʀ 𝐈ɴᴅɪᴀ 𝐖ᴀʟᴇ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇮🇳 ₊⁺⋆.˚",
        " ོ༘₊⁺🇯🇵 ₊⁺⋆.˚ 𝐓ᴇʀᴇ 𝐆𝐂 𝐌ᴇɪɴ 𝐌𝐚𝐫𝐜𝐨 𝐁ᴏss 𝐀ᴜʀ 𝐉ᴀᴘᴀɴ 𝐖ᴀʟᴇ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇯🇵 ₊⁺⋆.˚",
        " ₊⁺🇺🇸 ₊⁺⋆.˚ 𝐓ᴇʀᴇ 𝐆𝐂 𝐌ᴇɪɴ 𝐃ɪᴘᴇ𝐬𝐡𝐱𝐦𝐚𝐫𝐜𝐨 𝐀ᴜʀ 𝐔𝐒𝐀 𝐖ᴀʟᴇ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇺🇸 ₊⁺⋆.˚",
        " ོ༘₊⁺🇬🇧 ₊⁺⋆.˚ 𝐓ᴇʀᴇ 𝐆𝐂 𝐌ᴇɪɴ 𝐃ɪᴘᴇ𝐬𝐡 𝐁ᴏss 𝐀ᴜʀ 𝐔𝐊 𝐖ᴀʟᴇ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇬🇧 ₊⁺⋆.˚",
        " ོ༘₊⁺🇰🇷 ₊⁺⋆.˚ 𝐓ᴇʀᴇ 𝐆𝐂 𝐌ᴇɪɴ 𝐌𝐚𝐫𝐜𝐨 𝐁ᴏss 𝐀ᴜʀ 𝐊ᴏʀᴇᴀ 𝐖ᴀʟᴇ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇰🇷 ₊⁺⋆.˚",
        " ོ༘₊⁺🇩🇪 ₊⁺⋆.˚ 𝐓ᴇʀᴇ 𝐆𝐂 𝐌ᴇɪɴ 𝐃ɪᴘᴇ𝐬𝐡𝐱𝐦𝐚𝐫𝐜𝐨 𝐀ᴜʀ 𝐆ᴇʀᴍᴀɴʏ 𝐖ᴀʟᴇ 𝐂ʜɪʟʟ 𝐊ᴀʀ 𝐑ʜᴇ ོ༘₊⁺🇩🇪 ₊⁺⋆.˚"
    ],
    "heart_replies": [
        "𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐃ɪᴘᴇ𝐬𝐡 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐊𝐈𝐍𝐆 𝐎𝐅 𝐓𝐆 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐌𝐚𝐫𝐜𝐨 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐑𝐔𝐋𝐄𝐑 𝐎𝐅 𝐓𝐆 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐃ɪᴘᴇ𝐬𝐡𝐱𝐦𝐚𝐫𝐜𝐨 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 -/- ⋆˚💛 ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐃ɪᴘᴇ𝐬𝐡 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐒𝐔𝐏𝐑𝐄𝐌𝐄 -/- ⋆˚💚 ݁˖⭑.ᐟ",
        "𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ 𝐌𝐚𝐫𝐜𝐨 ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝐔𝐍𝐒𝐓𝐎𝐏𝐏𝐀𝐁𝐋𝐄 -/- ⋆˚💙 ݁˖⭑.ᐟ"
    ],
    "attack_list": [
        "⚔️ Teri aukat nahi Dipesh se ladhne ki 😂🔥",
        "💥 Chal bhaag yahan se warna Marco pel dega 🤣⚔️",
        "🗡️ Dipeshxmarco aaya hai sunta nahi kya 👑😈",
        "⚡ Dipesh ke saamne aake dikhao himmat hai toh 😎💪",
        "🔥 Marco Attack mode on — teri khair nahi aaj 😡⚔️",
        "💀 Dipeshxmarco ka kahar shuru ho chuka hai 😂🔥",
        "⚔️ Chal 1v1 kar le Dipesh dikhata hai kaun boss hai 👊😤",
        "💥 Beta ye territory Marco ki hai nikal yahan se 🏴‍☠️⚡",
        "🗡️ Aukaat hai toh Dipeshxmarco ke saamne aa 😈💀",
        "⚡ Tu keyboard warrior hai, Dipesh asli king hai 😂👊"
    ],
    "roast_list": [
        "🔥 Teri zindagi ek bakwas webseries ki tarah hai — Dipesh ne 1 sec mein flop kar diya 😂📺",
        "🤣 Bhai teri personality sada hua pyaz jaisi hai — Marco dekh ke has pada 🧅💀",
        "😹 Tu itna slow hai ke Dipeshxmarco bot tujhe 100 baar cross kar gaya 🦟😂",
        "🔥 Tujhe dekh ke pata chalta hai — Marco se darr ke jeena kya hota hai 😂💀",
        "😹 Beta tu Google Maps pe search kare toh bhi Dipesh ke aage zero aayega 🗺️😈",
        "🔥 Teri IQ level negative hai — Marco ke calculator mein error aata hai 🧮😂",
        "🤣 Tu chhata hua papad hai — Dipeshxmarco ke touch karte hi toot gaya 😹🔥",
        "😹 Bhai teri aukat itni hai ke mirror bhi Marco ka naam leta hai 🪞😂"
    ],
    "motivation_quotes": [
        "Believe you can and you're halfway there. – Dipeshxmarco",
        "The only way to do great work is to love what you do. – Steve Jobs",
        "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "It does not matter how slowly you go as long as you do not stop."
    ],
    "truths": [
        "What is the biggest lie you've ever told?",
        "Have you ever cheated on a test?",
        "What is the most embarrassing thing you've done in public?",
        "Who is your secret crush?"
    ],
    "dares": [
        "Do 20 push-ups right now.",
        "Sing the national anthem loudly.",
        "Send a random emoji to your last chat.",
        "Swap your profile picture with a Dipeshxmarco banner for an hour."
    ],
    "shayaris": [
        "तुम्हें देखा तो ये ख़याल आया,\nज़िन्दगी धूप, Dipeshxmarco घना साया।",
        "मोहब्बत की राहें मुश्किल हैं,\nफिर भी Dipesh और Marco ने ये राह चुनी है।",
        "तेरी यादों में बीती है रात,\nसुबह हुई तो फिर से Marco की बात।"
    ],
    "jokes": [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What do you call a bear with no teeth? A gummy bear!",
        "What do you call fake spaghetti? An impasta!"
    ],
    "quotes": [
        "The only limit to our realization of tomorrow is our doubts of today.",
        "In the middle of difficulty lies opportunity. – Dipeshxmarco",
        "Do or do not. There is no try."
    ]
}

COUNTRY_EMOJIS = ["🇮🇳", "🇺🇸", "🇬🇧", "🇨🇦", "🇦🇺", "🇩🇪", "🇫🇷", "🇯🇵", "🇰🇷", "🇨🇳", "🇷🇺", "🇧🇷", "🇮🇹", "🇪🇸", "🇦🇪", "🇸🇦"]
RANDOM_EMOJIS = ["🔥", "⚡", "✨", "🌟", "⭐", "💫", "🌙", "☀️", "❤️", "🧡", "💛", "💚", "💙", "💜", "👑", "💀", "🚀"]

# ════════════════════════════════════════════════════════════════════════════════
#   DATABASE MANAGER (WITH BUILT-IN TEXT BANKS)
# ════════════════════════════════════════════════════════════════════════════════
class DBManager:
    def __init__(self, filename="hosting_db.json"):
        self.filename = filename
        self.data = {
            "users": {},
            "accounts": {},
            "blocked": [],
            "sudo": [],
            "bot_settings": {"is_on": True},
            "welcome_video": None,
            "text_banks": {k: list(v) for k, v in DEFAULT_TEXT_BANKS.items()}
        }
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
                if "text_banks" not in self.data:
                    self.data["text_banks"] = {k: list(v) for k, v in DEFAULT_TEXT_BANKS.items()}
                else:
                    for k, v in DEFAULT_TEXT_BANKS.items():
                        if k not in self.data["text_banks"] or not self.data["text_banks"][k]:
                            self.data["text_banks"][k] = list(v)
                self.save()
            except Exception as e:
                logger.error(f"DB Load Error: {e}")

    def save(self):
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"DB Save Error: {e}")

    def get_text_bank(self, category: str) -> list:
        return self.data.get("text_banks", {}).get(category, DEFAULT_TEXT_BANKS.get(category, []))

    def get_all_text_banks(self) -> dict:
        return self.data.get("text_banks", DEFAULT_TEXT_BANKS)

    def add_bank_text(self, category: str, text: str):
        if "text_banks" not in self.data:
            self.data["text_banks"] = {}
        if category not in self.data["text_banks"]:
            self.data["text_banks"][category] = []
        self.data["text_banks"][category].append(text)
        self.save()

    def delete_bank_text(self, category: str, idx: int):
        if category in self.data.get("text_banks", {}):
            if 0 <= idx < len(self.data["text_banks"][category]):
                self.data["text_banks"][category].pop(idx)
                self.save()
                return True
        return False

    def reset_text_banks(self):
        self.data["text_banks"] = {k: list(v) for k, v in DEFAULT_TEXT_BANKS.items()}
        self.save()

    def is_sudo(self, uid, owner_id):
        return int(uid) == int(owner_id) or int(uid) in self.data.get("sudo", [])

    def is_blocked(self, uid):
        return int(uid) in self.data.get("blocked", [])

    def user_exists(self, uid):
        return str(uid) in self.data.get("users", {})

    def save_user_meta(self, uid, meta):
        uid = str(uid)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {}
        self.data["users"][uid].update(meta)
        self.save()

    def get_accounts(self, uid):
        uid = str(uid)
        accs = self.data["accounts"].get(uid, {})
        return list(accs.values())

    def get_account(self, uid, slot):
        uid = str(uid)
        return self.data["accounts"].get(uid, {}).get(str(slot))

    def add_account(self, uid, acc_dict):
        uid = str(uid)
        if uid not in self.data["accounts"]:
            self.data["accounts"][uid] = {}
        self.data["accounts"][uid][str(acc_dict["slot"])] = acc_dict
        self.save()

    def remove_account(self, uid, slot):
        uid = str(uid)
        if uid in self.data["accounts"] and str(slot) in self.data["accounts"][uid]:
            del self.data["accounts"][uid][str(slot)]
            self.save()

    def get_welcome_video(self):
        return self.data.get("welcome_video")

    def set_welcome_video(self, data):
        self.data["welcome_video"] = data
        self.save()

    def remove_welcome_video(self):
        self.data["welcome_video"] = None
        self.save()

    def hosted_count(self):
        return sum(len(accs) for accs in self.data["accounts"].values())

    def get_all_users(self):
        return list(self.data["users"].keys())

    def user_count(self):
        return len(self.data["users"])

    def get_blocked(self):
        return self.data.get("blocked", [])

    def block_user(self, uid):
        uid = int(uid)
        if uid not in self.data["blocked"]:
            self.data["blocked"].append(uid)
            self.save()

    def unblock_user(self, uid):
        uid = int(uid)
        if uid in self.data["blocked"]:
            self.data["blocked"].remove(uid)
            self.save()

    def get_sudo_users(self):
        return self.data.get("sudo", [])

    def add_sudo(self, uid):
        uid = int(uid)
        if uid not in self.data["sudo"]:
            self.data["sudo"].append(uid)
            self.save()

    def remove_sudo(self, uid):
        uid = int(uid)
        if uid in self.data["sudo"]:
            self.data["sudo"].remove(uid)
            self.save()

    def is_bot_on(self):
        return self.data.get("bot_settings", {}).get("is_on", True)

    def set_bot_settings(self, settings):
        if "bot_settings" not in self.data:
            self.data["bot_settings"] = {}
        self.data["bot_settings"].update(settings)
        self.save()

db = DBManager()

# ════════════════════════════════════════════════════════════════════════════════
#   USERBOT ENGINE REGISTRATION (DIPESHXMARCO COMPLETE LOGIC)
# ════════════════════════════════════════════════════════════════════════════════
def register_userbot_engine(client: TelegramClient, user_id: int):

    def get_bank(name):
        return db.get_text_bank(name)

    def get_all_combined_texts():
        banks = db.get_all_text_banks()
        combined = []
        for k in ["reply_texts", "GAALI_LIST", "fun_texts", "flag_texts", "heart_replies", "attack_list", "roast_list"]:
            combined.extend(banks.get(k, []))
        return combined if combined else ["🔥 DIPESHXMARCO ULTIMATE ENGINE 🔥"]

    class LocalBotState:
        def __init__(self):
            self.bot_on = True
            self.flow_mode = False
            self.saved_texts = []
            self.spray_delay = 0.5
            self.auto_reply_on = False
            self.warnings = {}
            self.active_tasks = {}
            self.safe_users = set()
            self.safe_usernames = {}
            self.auto_delete_chats = {}
            self.delete_target_users = defaultdict(set)
            self.delete_target_usernames = defaultdict(set)
            self.delete_delay = 0.05
            self.autoswipe_active = {}
            self.adv_spam_active = {}
            self.namechange_active = {}
            self.raid_active = {}
            self.blitz_active = {}
            self.react_active = {}
            self.locked_titles = {}
            self.swipe_targets = defaultdict(dict)
            self.msg_log = defaultdict(lambda: deque())
            self.offenses = defaultdict(int)
            self.locked_groups = set()
            self.locked_chat = set()
            self.locked_name_change = set()
            self.emergency_active = {}
            self.metrics = {"start": time.monotonic(), "msg": 0, "mutes": 0, "swipes": 0}
            self.namechange_delays = {}

            self.flow_delay = 0.2
            self.flow_count = 30
            self.fast_gc_trigger = None
            self.fast_gc_template = None
            self.boost_mode = False
            self.critical_mode = False

            self.normal_cfg = dict(SPAM=5, WINDOW=6)
            self.boost_cfg = dict(SPAM=3, WINDOW=3)
            self.crit_cfg = dict(SPAM=2, WINDOW=2)
            self.cfg = self.normal_cfg.copy()
            self.mute_table = (300, 900, 1800, 3600, 21600)

        def is_user_safe(self, uid, username=None):
            if uid in self.safe_users or uid == user_id:
                return True
            if username and username.lower() in self.safe_usernames:
                return True
            return False

        def should_delete_user(self, chat_id, uid, username=None):
            if chat_id not in self.delete_target_users:
                return False
            if uid in self.delete_target_users[chat_id]:
                return True
            if username and chat_id in self.delete_target_usernames:
                if username.lower() in self.delete_target_usernames[chat_id]:
                    return True
            return False

    state = LocalBotState()

    async def is_authorized(event):
        if event.raw_text and event.raw_text.startswith(("/on", ".on")): return True
        if not state.bot_on: return False
        if event.out or event.sender_id == user_id: return True

        sender_id = getattr(event, 'sender_id', None)
        if not sender_id: return False

        username = None
        try:
            sender = await event.get_sender()
            if hasattr(sender, 'username'): username = sender.username
        except: pass

        if state.is_user_safe(sender_id, username): return True
        return False

    def command(cmd):
        def decorator(func):
            @client.on(events.NewMessage(pattern=rf"^[/.]{cmd}(?:\b|$)"))
            async def handler(event):
                if not await is_authorized(event): return
                try: await func(event)
                except Exception as e: await event.reply(f"❌ Error: {e}")
            return handler
        return decorator

    def flow_command(cmd):
        def decorator(func):
            @client.on(events.NewMessage(pattern=rf"^[/.]{cmd}(?:\b|$)"))
            async def handler(event):
                if not await is_authorized(event): return
                if not state.flow_mode: return await event.reply("❌ Flow bot is OFF. Use `.switch` to enable.")
                try: await func(event)
                except Exception as e: await event.reply(f"❌ Error: {e}")
            return handler
        return decorator

    async def get_target(event):
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            try:
                return await client.get_entity(reply_msg.sender_id)
            except: pass

        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2:
            await event.reply("⚠️ Please specify a target username or ID, or reply to a message.")
            return None
        target_str = args[1].strip()
        if target_str.startswith("@"): target_str = target_str[1:]
        try:
            if target_str.isdigit(): return await client.get_entity(int(target_str))
            else: return await client.get_entity(target_str)
        except Exception as e:
            await event.reply(f"❌ Could not find user: {e}")
            return None

    async def get_target_from_str(event, target_str):
        if target_str.startswith("@"): target_str = target_str[1:]
        try:
            if target_str.isdigit(): return await client.get_entity(int(target_str))
            else: return await client.get_entity(target_str)
        except Exception as e:
            await event.reply(f"❌ Could not find user: {e}")
            return None

    async def get_user_from_arg(event):
        return await get_target(event)

    # ------------------------- BACKGROUND GUARDS -------------------------
    async def smart_mute(chat_id, target_uid):
        if target_uid == user_id: return
        state.offenses[(chat_id, target_uid)] += 1
        state.metrics["mutes"] += 1
        duration = state.mute_table[min(state.offenses[(chat_id, target_uid)] - 1, 4)]
        try: await client(EditBannedRequest(chat_id, target_uid, ChatBannedRights(send_messages=True, until_date=int(time.time()) + duration)))
        except: pass

    @client.on(events.NewMessage(incoming=True))
    async def auto_delete_handler(event):
        if not state.bot_on: return
        chat_id = event.chat_id
        if not state.auto_delete_chats.get(chat_id, False): return

        if hasattr(event, 'action') and event.action is not None:
            try:
                await asyncio.sleep(state.delete_delay)
                await event.delete()
            except: pass
            return

        if not event.sender_id: return
        uid = event.sender_id
        username = getattr(getattr(event, 'sender', None), 'username', None)

        if chat_id in state.delete_target_users and state.delete_target_users[chat_id]:
            if state.should_delete_user(chat_id, uid, username):
                try:
                    await asyncio.sleep(state.delete_delay)
                    await event.delete()
                except: pass
            return

        if not state.is_user_safe(uid, username):
            try:
                await asyncio.sleep(state.delete_delay)
                await event.delete()
            except: pass

    @client.on(events.NewMessage(incoming=True))
    async def global_react_handler(event):
        if not state.bot_on: return
        if event.chat_id in state.react_active:
            try:
                emoji = random.choice(RANDOM_EMOJIS[:10])
                await event.react(emoji)
            except: pass

    @client.on(events.NewMessage(incoming=True))
    async def message_guard(event):
        if not state.bot_on: return
        if event.text and event.text.startswith('.'): return
        state.metrics["msg"] += 1
        uid, cid = event.sender_id, event.chat_id
        if uid == user_id: return

        if state.critical_mode:
            await smart_mute(cid, uid)
            return

        now = time.monotonic()
        log = state.msg_log[(cid, uid)]
        log.append(now)
        while log and now - log[0] > state.cfg["WINDOW"]: log.popleft()
        if len(log) >= state.cfg["SPAM"]:
            await smart_mute(cid, uid)
            return

        if cid in state.swipe_targets and uid in state.swipe_targets[cid]:
            state.metrics["swipes"] += 1
            asyncio.create_task(event.reply(state.swipe_targets[cid][uid]))

    @client.on(events.NewMessage(incoming=True))
    async def chat_lock_handler(event):
        if not state.bot_on: return
        if event.chat_id in state.locked_chat and event.sender_id != user_id:
            try: await event.delete()
            except: pass

    @client.on(events.ChatAction)
    async def title_guard(event):
        if not state.bot_on: return
        if event.chat_id in state.locked_titles and getattr(event, 'user_id', None) != user_id:
            try:
                await client(EditChatTitleRequest(event.chat_id, state.locked_titles[event.chat_id]))
                if hasattr(event, 'user_id'): await smart_mute(event.chat_id, event.user_id)
            except: pass

    @client.on(events.ChatAction)
    async def namechange_lock_handler(event):
        if not state.bot_on: return
        if event.chat_id in state.locked_name_change and getattr(event, 'user_id', None) != user_id:
            if event.chat_id in state.locked_titles:
                try: await client(EditChatTitleRequest(event.chat_id, state.locked_titles[event.chat_id]))
                except: pass

    @client.on(events.NewMessage(incoming=True))
    async def adv_multireply_handler(event):
        if not state.bot_on: return
        chat_id = event.chat_id
        if chat_id not in state.autoswipe_active: return
        swipe_data = state.autoswipe_active[chat_id]
        if isinstance(swipe_data, str) and swipe_data.startswith("MULTI:"):
            parts = swipe_data.split(":", 2)
            if len(parts) == 3:
                try:
                    times = int(parts[1])
                    for _ in range(times):
                        await event.reply(parts[2])
                        await asyncio.sleep(0.05)
                except: pass
        elif isinstance(swipe_data, str) and not swipe_data.startswith("MULTI:") and not swipe_data.startswith("RAID:"):
            try: await event.reply(swipe_data)
            except: pass

    @client.on(events.NewMessage(incoming=True))
    async def global_raid_handler(event):
        if not state.bot_on or event.out: return
        chat_id = event.chat_id
        uid = event.sender_id
        if not uid: return

        if chat_id in state.raid_active and uid in state.raid_active[chat_id]:
            raid_data = state.raid_active[chat_id][uid]
            texts = get_bank(raid_data["bank"]) if "bank" in raid_data else raid_data.get("texts", ["🔥 DIPESHXMARCO 🔥"])
            if texts:
                try: await event.reply(random.choice(texts))
                except: pass

    # ------------------------- BASE COMMANDS -------------------------
    @command("on")
    async def cmd_on(event):
        state.bot_on = True
        await event.reply("✅ **Dipeshxmarco** is now **ON**.")

    @command("off")
    async def cmd_off(event):
        state.bot_on = False
        await event.reply("🔴 **Dipeshxmarco** is now **OFF**.")

    @command("alive")
    async def cmd_alive(event):
        up = int(time.monotonic() - state.metrics["start"])
        h, r = divmod(up, 3600); m, s = divmod(r, 60)
        await event.reply(
            f"╔════════════════════════════════════╗\n"
            f"║ ⚡ **𝐃𝐈𝐏𝐄𝐒𝐇𝐗𝐌𝐀𝐑𝐂𝐎 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄** ⚡ ║\n"
            f"╚════════════════════════════════════╝\n\n"
            f"👑 **Creators:** `Dipesh & Marco`\n"
            f"🟢 **State:** `ONLINE & READY`\n"
            f"🌊 **Flow Mode:** `{'ON' if state.flow_mode else 'OFF'}`\n"
            f"⏱️ **Uptime:** `{h}h {m}m {s}s`\n"
            f"🛠️ **Explore:** `.menu` | `.flowmenu` | `.advmenu`"
        )

    @command("ping")
    async def cmd_ping(event):
        start = time.perf_counter()
        msg = await event.reply("🏓 **Dipeshxmarco Pinging...**")
        end = time.perf_counter()
        await msg.edit(f"🏓 **Pong!** 🌀 Latency: `{(end - start) * 1000:.2f} ms`")

    @command("echo")
    async def cmd_echo(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) > 1: await event.reply(args[1])
        else: await event.reply("ℹ️ Usage: `.echo <text>`")

    @command("stats")
    async def cmd_stats_ub(event):
        up = int(time.monotonic() - state.metrics["start"])
        d, r = divmod(up, 86400); h, r = divmod(r, 3600); m, s = divmod(r, 60)
        await event.reply(
            f"📊 **Dipeshxmarco Stats**\n"
            f"• Uptime: `{d}d {h}h {m}m {s}s`\n"
            f"• State: `{'ON' if state.bot_on else 'OFF'}`\n"
            f"• Flow Mode: `{'ON' if state.flow_mode else 'OFF'}`\n"
            f"• API ID: `{TELEGRAM_API_ID}`"
        )

    @command("info")
    async def cmd_info(event):
        chat = await event.get_chat()
        sender = await event.get_sender()
        await event.reply(
            f"ℹ️ **Chat Info**\n• ID: `{event.chat_id}`\n• Title: `{getattr(chat, 'title', 'N/A')}`\n\n"
            f"👤 **Sender**\n• ID: `{sender.id}`\n• Name: `{utils.get_display_name(sender)}`"
        )

    @command("restart")
    async def cmd_restart_ub(event):
        await event.reply("🔄 Restart request received. Use `/restart` in the Dipeshxmarco Hoster Bot or Web Panel.")

    @command("switch")
    async def cmd_switch(event):
        state.flow_mode = not state.flow_mode
        await event.reply(f"🔄 **Dipeshxmarco Flow Mode** is now **{'ON' if state.flow_mode else 'OFF'}**.\nUse `.flowmenu` for flow commands.")

    @command("react")
    async def cmd_react(event):
        state.react_active[event.chat_id] = True
        msg = await event.respond("🔄 **INITIALIZING DIPESHXMARCO REACT ENGINE...**")
        await asyncio.sleep(0.3)
        await msg.edit("✅ **REACT MODE ON**\nReacting to all messages in this chat!")

    @command("sreact")
    async def cmd_sreact(event):
        if event.chat_id in state.react_active:
            del state.react_active[event.chat_id]
            await event.respond("✅ **REACT MODE OFF**")
        else:
            await event.respond("ℹ️ React mode is not active here.")

    # ------------------------- RAID & ROAST COMMANDS -------------------------
    async def start_raid(event, bank_name, raid_type):
        user = await get_target(event)
        if not user: return
        chat_id = event.chat_id
        state.raid_active.setdefault(chat_id, {})[user.id] = {"bank": bank_name, "type": raid_type}
        await event.reply(f"⚡ **Dipeshxmarco {raid_type.upper()}** started on `{utils.get_display_name(user)}`!")

    async def stop_raid(event, raid_type):
        chat_id = event.chat_id
        stopped = False
        if chat_id in state.raid_active:
            to_remove = [uid for uid, data in state.raid_active[chat_id].items() if data["type"] == raid_type]
            for uid in to_remove:
                del state.raid_active[chat_id][uid]
                stopped = True
            if not state.raid_active[chat_id]:
                del state.raid_active[chat_id]

        if stopped: await event.reply(f"✅ **Dipeshxmarco {raid_type.capitalize()}** stopped.")
        else: await event.reply(f"ℹ️ No active {raid_type} raid in this chat.")

    @command("reply")
    async def cmd_reply(event): await start_raid(event, "reply_texts", "reply")
    @command("sreply")
    async def cmd_sreply(event): await stop_raid(event, "reply")

    @command("rr")
    async def cmd_rr(event): await start_raid(event, "GAALI_LIST", "rr")
    @command("srr")
    async def cmd_srr(event): await stop_raid(event, "rr")

    @command("flag")
    async def cmd_flag(event): await start_raid(event, "flag_texts", "flag")
    @command("sflag")
    async def cmd_sflag(event): await stop_raid(event, "flag")

    @command("hrr")
    async def cmd_hrr(event): await start_raid(event, "heart_replies", "hrr")
    @command("shrr")
    async def cmd_shrr(event): await stop_raid(event, "hrr")

    @command("replygod")
    async def cmd_replygod(event):
        user = await get_target(event)
        if not user: return
        combined = get_bank("attack_list") + get_bank("roast_list")
        state.raid_active.setdefault(event.chat_id, {})[user.id] = {"texts": combined, "type": "replygod"}
        await event.reply(f"😈 **Dipeshxmarco God Mode** started on `{utils.get_display_name(user)}`!")

    @command("sgod")
    async def cmd_sgod(event): await stop_raid(event, "replygod")

    @command("replyraid")
    async def reply_raid_cmd(event): await start_raid(event, "GAALI_LIST", "replyraid")
    @command("stopreplyraid")
    async def stop_reply_raid_cmd(event): await stop_raid(event, "replyraid")

    @command("superraid")
    async def cmd_superraid(event):
        user = await get_target(event)
        if not user: return
        state.raid_active.setdefault(event.chat_id, {})[user.id] = {"texts": get_all_combined_texts(), "type": "superraid"}
        await event.reply(f"💥 **Dipeshxmarco Super Raid** started on `{utils.get_display_name(user)}`!")

    @command("stopsuper")
    async def cmd_stopsuper(event): await stop_raid(event, "superraid")

    @command("attack")
    async def cmd_attack_single(event):
        await event.reply(random.choice(get_bank("attack_list")))

    @command("roast")
    async def cmd_roast_single(event):
        await event.reply(random.choice(get_bank("roast_list")))

    async def limited_raid_loop(chat, user, text, count):
        try:
            for _ in range(count):
                try:
                    if getattr(user, 'username', None): await client.send_message(chat, f"{text} @{user.username}")
                    else: await client.send_message(chat, f"{text} {user.first_name}")
                except Exception: pass
                await asyncio.sleep(0.2)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("limited", None)

    @command("replydipesh")
    async def cmd_replydipesh(event):
        args = event.raw_text.split(maxsplit=3)
        if len(args) < 4: return await event.reply("⚠️ Usage: `.replydipesh @user <text> <count>`")
        try: count = int(args[3])
        except ValueError: return await event.reply("⚠️ Count must be a number.")
        user = await get_target_from_str(event, args[1])
        if not user: return
        if "limited" in state.active_tasks: state.active_tasks["limited"].cancel()
        state.active_tasks["limited"] = asyncio.create_task(limited_raid_loop(event.chat, user, args[2], count))
        await event.reply(f"✅ **Dipeshxmarco Limited Raid** started on `{utils.get_display_name(user)}` for {count} messages.")

    @command("replymarco")
    async def cmd_replymarco(event): await cmd_replydipesh(event)

    @command("sstop")
    async def cmd_sstop(event):
        if "limited" in state.active_tasks:
            state.active_tasks["limited"].cancel()
            await event.reply("✅ Limited raid stopped.")
        else: await event.reply("ℹ️ No limited raid running.")

    @command("raid")
    async def cmd_raid(event):
        args = event.text.strip().split()
        if len(args) < 2: return await event.reply("**Usage:** `.raid <count>`")
        try: count = int(args[1])
        except: return await event.respond("❌ **Count must be a valid number!**")

        chat_id = event.chat_id
        if "dxm_raid" in state.active_tasks: return await event.reply("⚠️ A Dipeshxmarco raid is already running. Use `.stopraid` first.")

        async def dxm_raid_loop():
            try:
                raid_pool = get_bank("RAID_TEXTS")
                for _ in range(count):
                    if "dxm_raid" not in state.active_tasks: break
                    try: await client.send_message(chat_id, random.choice(raid_pool))
                    except: pass
                    await asyncio.sleep(0.1)
                if "dxm_raid" in state.active_tasks:
                    await client.send_message(chat_id, "✅ **DIPESHXMARCO RAID SUCCESSFULLY COMPLETED!**")
            except asyncio.CancelledError: pass
            finally: state.active_tasks.pop("dxm_raid", None)

        state.active_tasks["dxm_raid"] = asyncio.create_task(dxm_raid_loop())
        msg = await event.respond("🚀 **DIPESHXMARCO PREPARING TO RAID...**")
        await asyncio.sleep(0.3)
        await msg.edit(f"🔥 **DIPESHXMARCO RAID INITIATED: {count} MESSAGES!**")

    @command("stopraid")
    async def cmd_stopraid(event):
        if "dxm_raid" in state.active_tasks:
            state.active_tasks["dxm_raid"].cancel()
            await event.reply("🛑 **DIPESHXMARCO RAID FORCE STOPPED!**")
        else: await event.reply("ℹ️ No active Dipeshxmarco raid.")

    # ------------------------- SPRAY COMMANDS -------------------------
    async def spray_task(chat, text, count, delay):
        try:
            for _ in range(count):
                try: await client.send_message(chat, text)
                except: pass
                await asyncio.sleep(delay)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("spray", None)

    async def rspray_task(chat, text_list, count, delay):
        try:
            for _ in range(count):
                try: await client.send_message(chat, random.choice(text_list))
                except: pass
                await asyncio.sleep(delay)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("spray", None)

    async def multispray_task(chat, lines, delay):
        try:
            while "spray" in state.active_tasks:
                for line in lines:
                    if "spray" not in state.active_tasks: break
                    try: await client.send_message(chat, line)
                    except: pass
                    await asyncio.sleep(delay)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("spray", None)

    @command("spray")
    async def cmd_spray(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.spray <text>`")
        if "spray" in state.active_tasks: return await event.reply("⚠️ A spray is already running.")
        state.active_tasks["spray"] = asyncio.create_task(spray_task(event.chat, args[1], 10, state.spray_delay))
        await event.reply(f"✅ Spray started for 10 messages with delay {state.spray_delay}s.")

    @command("dspray")
    async def cmd_dspray(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.dspray <text>`")
        try:
            async for msg in client.iter_messages(event.chat, limit=10):
                await msg.delete(); await asyncio.sleep(0.1)
        except Exception: pass
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        state.active_tasks["spray"] = asyncio.create_task(spray_task(event.chat, args[1], 10, state.spray_delay))
        await event.reply("✅ Deleted 10 messages and started Dipeshxmarco spray.")

    @command("tspray")
    async def cmd_tspray(event):
        args = event.raw_text.split(maxsplit=3)
        if len(args) < 4: return await event.reply("⚠️ Usage: `.tspray <count> <delay_sec> <text>`")
        try: count, delay, text = int(args[1]), float(args[2]), args[3]
        except ValueError: return await event.reply("⚠️ Count/delay must be numbers.")
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        state.active_tasks["spray"] = asyncio.create_task(spray_task(event.chat, text, count, delay))
        await event.reply(f"✅ Timed spray started: {count} messages.")

    @command("rspray")
    async def cmd_rspray(event):
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        text_list = state.saved_texts if state.saved_texts else get_all_combined_texts()
        state.active_tasks["spray"] = asyncio.create_task(rspray_task(event.chat, text_list, 20, state.spray_delay))
        await event.reply("✅ Dipeshxmarco Random Spray started (20 msgs).")

    @command("multispray")
    async def cmd_multispray(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.multispray <t1|t2|...>`")
        lines = [line.strip() for line in args[1].split("|") if line.strip()]
        if not lines: return await event.reply("⚠️ No valid lines.")
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        state.active_tasks["spray"] = asyncio.create_task(multispray_task(event.chat, lines, state.spray_delay))
        await event.reply(f"✅ Multi-spray started with {len(lines)} lines.")

    @command("countspray")
    async def cmd_countspray(event):
        args = event.raw_text.split(maxsplit=2)
        if len(args) < 3: return await event.reply("⚠️ Usage: `.countspray <count> <text>`")
        try: count, text = int(args[1]), args[2]
        except ValueError: return await event.reply("⚠️ Count must be a number.")
        if "spray" in state.active_tasks: state.active_tasks["spray"].cancel()
        state.active_tasks["spray"] = asyncio.create_task(spray_task(event.chat, text, count, state.spray_delay))
        await event.reply(f"✅ Count spray started: {count} messages.")

    @command("spraydelay")
    async def cmd_spraydelay(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply(f"ℹ️ Current spray delay: {state.spray_delay}s")
        try:
            val = float(args[1])
            if val < 0.1: return await event.reply("⚠️ Min delay 0.1s")
            state.spray_delay = val
            await event.reply(f"✅ Spray delay set to {state.spray_delay}s")
        except ValueError: await event.reply("⚠️ Invalid number.")

    @command("stopspray")
    async def cmd_stopspray(event):
        if "spray" in state.active_tasks:
            state.active_tasks["spray"].cancel()
            await event.reply("✅ Spray stopped.")
        else: await event.reply("ℹ️ No active spray.")

    # ------------------------- ADVANCED SPAM -------------------------
    @command("advspam")
    async def advspam_cmd(event):
        args = event.text.strip().split(None, 2)
        if len(args) < 3: return await event.respond("**Usage:** `.advspam <mode> <text>`\n**Modes:** fast, medium, slow, burst, random, tsunami, nightmare")
        mode, text = args[1].lower(), args[2]
        chat_id = event.chat_id
        valid_modes = ['fast', 'medium', 'slow', 'burst', 'random', 'tsunami', 'nightmare']
        if mode not in valid_modes: return await event.respond("❌ **Invalid mode!**")

        state.adv_spam_active[chat_id] = f"{mode}:{text}"
        msg = await event.respond("🚀 **PREPARING DIPESHXMARCO SPAM ENGINE...**")
        await asyncio.sleep(0.3)
        await msg.edit(f"📢 **DIPESHXMARCO SPAM ON:** {mode.upper()}")

        async def spam_task():
            while chat_id in state.adv_spam_active:
                try:
                    spam_data = state.adv_spam_active[chat_id]
                    if ':' not in spam_data: break
                    current_mode, spam_text = spam_data.split(':', 1)

                    if current_mode == 'fast': await client.send_message(chat_id, spam_text); await asyncio.sleep(0.1)
                    elif current_mode == 'medium': await client.send_message(chat_id, spam_text); await asyncio.sleep(0.5)
                    elif current_mode == 'slow': await client.send_message(chat_id, spam_text); await asyncio.sleep(2)
                    elif current_mode == 'burst':
                        for _ in range(10): await client.send_message(chat_id, spam_text); await asyncio.sleep(0.01)
                        await asyncio.sleep(5)
                    elif current_mode == 'random': await client.send_message(chat_id, spam_text); await asyncio.sleep(random.uniform(0.1, 3.0))
                    elif current_mode == 'tsunami':
                        for _ in range(50): await client.send_message(chat_id, spam_text); await asyncio.sleep(0.01)
                        await asyncio.sleep(10)
                    elif current_mode == 'nightmare':
                        for _ in range(5): await client.send_message(chat_id, spam_text); await asyncio.sleep(0.01)
                        await asyncio.sleep(1)
                except FloodWaitError as e: await asyncio.sleep(e.seconds)
                except Exception: continue
            state.adv_spam_active.pop(chat_id, None)

        state.active_tasks[f"advspam_{chat_id}"] = asyncio.create_task(spam_task())

    @command("stopadvspam")
    async def stopadvspam_cmd(event):
        chat_id = event.chat_id
        if chat_id in state.adv_spam_active:
            del state.adv_spam_active[chat_id]
            if f"advspam_{chat_id}" in state.active_tasks: state.active_tasks[f"advspam_{chat_id}"].cancel()
            await event.respond("✅ **DIPESHXMARCO ADV SPAM OFF**")

    @command("spam")
    async def spam_alias(event): await advspam_cmd(event)

    # ------------------------- TEXT MANAGER -------------------------
    @command("addtext")
    async def cmd_addtext(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.addtext <text>`")
        state.saved_texts.append(args[1])
        db.add_bank_text("reply_texts", args[1])
        await event.reply(f"✅ Text added to local & global Dipeshxmarco DB! Total local: {len(state.saved_texts)}")

    @command("listtexts")
    async def cmd_listtexts(event):
        if not state.saved_texts: return await event.reply("ℹ️ No custom saved texts.")
        text_list = "\n".join([f"{i+1}. {t[:50]}..." if len(t)>50 else f"{i+1}. {t}" for i,t in enumerate(state.saved_texts)])
        await event.reply(f"📝 **Saved Texts ({len(state.saved_texts)})**\n{text_list}")

    @command("edittext")
    async def cmd_edittext(event):
        args = event.raw_text.split(maxsplit=2)
        if len(args) < 3: return await event.reply("⚠️ Usage: `.edittext <index> <new_text>`")
        try:
            idx = int(args[1]) - 1
            if idx < 0 or idx >= len(state.saved_texts): return await event.reply("⚠️ Invalid index.")
            state.saved_texts[idx] = args[2]
            await event.reply(f"✅ Text {idx+1} updated.")
        except ValueError: await event.reply("⚠️ Index must be a number.")

    @command("deltext")
    async def cmd_deltext(event):
        args = event.raw_text.split(maxsplit=1)
        if len(args) < 2: return await event.reply("⚠️ Usage: `.deltext <index>`")
        try:
            idx = int(args[1]) - 1
            if idx < 0 or idx >= len(state.saved_texts): return await event.reply("⚠️ Invalid index.")
            removed = state.saved_texts.pop(idx)
            await event.reply(f"✅ Removed text: `{removed[:30]}...`")
        except ValueError: await event.reply("⚠️ Index must be a number.")

    @command("cleartext")
    async def cmd_cleartext(event):
        state.saved_texts.clear()
        await event.reply("✅ All custom saved texts cleared.")

    # ------------------------- ADMIN & SECURITY COMMANDS -------------------------
    @command("mute")
    async def cmd_mute(event):
        user = await get_user_from_arg(event)
        if not user: return
        if event.is_group:
            try:
                await client.edit_permissions(event.chat_id, user, ChatBannedRights(until_date=None, send_messages=True))
                await event.reply(f"🔇 Muted {utils.get_display_name(user)}.")
            except Exception as e: await event.reply(f"❌ Failed: {e}")
        else:
            state.delete_target_users[event.chat_id].add(user.id)
            state.auto_delete_chats[event.chat_id] = True
            await event.reply(f"🔇 Muted {utils.get_display_name(user)} in DM.")

    @command("unmute")
    async def cmd_unmute(event):
        user = await get_user_from_arg(event)
        if not user: return
        if event.is_group:
            try:
                await client.edit_permissions(event.chat_id, user, ChatBannedRights(until_date=None, send_messages=False))
                await event.reply(f"🔊 Unmuted {utils.get_display_name(user)}.")
            except Exception as e: await event.reply(f"❌ Failed: {e}")
        else:
            if event.chat_id in state.delete_target_users:
                state.delete_target_users[event.chat_id].discard(user.id)
            await event.reply(f"🔊 Unmuted {utils.get_display_name(user)} in DM.")

    @command("promote")
    async def cmd_promote(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        user = await get_user_from_arg(event)
        if not user: return
        try:
            await client.edit_admin(event.chat_id, user, ChatAdminRights(post_messages=True, invite_users=True, change_info=True, ban_users=True, pin_messages=True, manage_call=True, delete_messages=True))
            await event.reply(f"⬆️ Promoted {utils.get_display_name(user)}.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("demote")
    async def cmd_demote(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        user = await get_user_from_arg(event)
        if not user: return
        try:
            await client.edit_admin(event.chat_id, user, ChatAdminRights(post_messages=False, invite_users=False, change_info=False, ban_users=False, pin_messages=False, manage_call=False, delete_messages=False))
            await event.reply(f"⬇️ Demoted {utils.get_display_name(user)}.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("kick")
    async def cmd_kick(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        user = await get_user_from_arg(event)
        if not user: return
        try:
            await client.kick_participant(event.chat_id, user)
            await event.reply(f"👢 Kicked {utils.get_display_name(user)}.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    @command("ban")
    async def cmd_ban(event):
        if not event.is_group: return await event.reply("⚠️ Groups only.")
        user = await get_user_from_arg(event)
        if not user: return
        try:
            await client.edit_permissions(event.chat_id, user, ChatBannedRights(until_date=None, view_messages=True))
            await event.reply(f"🚫 Banned {utils.get_display_name(user)}.")
        except Exception as e: await event.reply(f"❌ Failed: {e}")

    # ------------------------- MENUS -------------------------
    @command("menu")
    async def cmd_menu(event):
        msg = await event.reply("🔄 **INITIALIZING DIPESHXMARCO MASTER MENU...**")
        await asyncio.sleep(0.2)
        menu = """
╔═══════════════════════════════════════════╗
║    👑  𝐃𝐈𝐏𝐄𝐒𝐇𝐗𝐌𝐀𝐑𝐂𝐎 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐌𝐄𝐍𝐔  👑    ║
╚═══════════════════════════════════════════╝

  📌 `.menu`      → Master Menu
  📌 `.flowmenu`  → Flow Bot Menu
  📌 `.advmenu`   → Advanced Security Menu
  📌 `.about`     → About Dipeshxmarco
  📌 `.alive`     → Check Engine Status

【 🛠️ 𝗕𝗔𝗦𝗜𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  `.on`, `.off`, `.ping`, `.echo`, `.stats`, `.info`, `.restart`, `.switch`

【 ⚔️ 𝗥𝗔𝗜𝗗 𝗘𝗡𝗚𝗜𝗡𝗘 (𝗗𝗜𝗣𝗘𝗦𝗛 & 𝗠𝗔𝗥𝗖𝗢) 】
  💬 Reply      → `.reply @user`    | `.sreply`
  🤣 RR         → `.rr @user`       | `.srr`
  🚩 Flag       → `.flag @user`     | `.sflag`
  💗 Heart      → `.hrr @user`      | `.shrr`
  😈 God        → `.replygod @user` | `.sgod`
  📌 Limited    → `.replydipesh @user <text> <count>` | `.sstop`
  ⚡ Super      → `.superraid @user`| `.stopsuper`
  🔥 DXM Raid   → `.raid <count>`   | `.stopraid`

【 💣 𝗦𝗣𝗔𝗠 𝗦𝗬𝗦𝗧𝗘𝗠 】
  ✦ `.spam <mode> <text>` (fast, medium, slow, burst, random, tsunami, nightmare)
  ✦ `.spray <text>` | `.dspray <text>` | `.tspray <n> <del> <t>`
  ✦ `.rspray` | `.multispray <t1|t2...>` | `.countspray <n> <text>`
  ✦ `.spraydelay <sec>` | `.stopspray` | `.stopadvspam`

【 📝 𝗧𝗘𝗫𝗧 𝗠𝗔𝗡𝗔𝗚𝗘𝗥 】
  `.addtext`, `.listtexts`, `.edittext`, `.deltext`, `.cleartext`

【 👑 𝗔𝗗𝗠𝗜𝗡 & 𝗨𝗧𝗜𝗟𝗜𝗧𝗬 】
  `.mute`, `.unmute`, `.promote`, `.demote`, `.kick`, `.ban`
  `.react`, `.sreact`, `.id`, `.tagall`, `.warn`, `.join`, `.autoreply`
  Fun: `.attack`, `.roast`, `.motivate`, `.truth`, `.dare`, `.shayari`, `.joke`, `.quote`

╔═══════════════════════════════════════════╗
║    ⚡  𝐃𝐢𝐩𝐞𝐬𝐡𝐱𝐦𝐚𝐫𝐜𝐨 — 𝐀𝐥𝐥 𝐑𝐢𝐠𝐡𝐭𝐬 𝐑𝐞𝐬𝐞𝐫𝐯𝐞𝐝   ║
╚═══════════════════════════════════════════╝
        """
        await msg.edit(menu)

    @command("advmenu")
    async def cmd_advmenu(event):
        menu = """
╔═══════════════════════════════════════════╗
║  🛡️ 𝐃𝐈𝐏𝐄𝐒𝐇𝐗𝐌𝐀𝐑𝐂𝐎 𝐀𝐃𝐕𝐀𝐍𝐂𝐄𝐃 𝐒𝐄𝐂𝐔𝐑𝐈𝐓𝐘 🛡️  ║
╚═══════════════════════════════════════════╝

【 🗑️ 𝗠𝗨𝗧𝗘 𝗖𝗢𝗡𝗧𝗥𝗢𝗟𝗦 】
  • `.sabchup` / `.speakall`
  • `.chup` / `.bol` (reply to user)
  • `.safe @user`

【 🔄 𝗡𝗔𝗠𝗘 & 𝗕𝗟𝗜𝗧𝗭 𝗖𝗢𝗡𝗧𝗥𝗢𝗟𝗦 】
  • `.namechange [mode] [ms]` (modes: time, emoji, owns, enters, dad)
  • `.namedelay <ms>` | `.stopnamechange`
  • `.blitz` | `.stopblitz`

【 🔐 𝗦𝗘𝗖𝗨𝗥𝗜𝗧𝗬 𝗟𝗢𝗖𝗞𝗦 】
  • `.lockname` | `.lockgroup` | `.unlockgroup`
  • `.lockchat` | `.unlockchat`
  • `.locknamechange` | `.unlocknamechange`

【 🛡️ 𝗣𝗥𝗢𝗧𝗘𝗖𝗧𝗜𝗢𝗡 & 𝗘𝗠𝗘𝗥𝗚𝗘𝗡𝗖𝗬 】
  • `.boost on/off` | `.assist on/off` | `.perf`
  • `.terminate` | `.killname`
  • `.dominate` | `.stopdominate`
  • `.emergency` | `.stopemergency`
  • `.makegc <name>` | `.lockswipe @user <text>` | `.hindivoice <text>`
        """
        await event.reply(menu)

    @command("flowmenu")
    async def cmd_flowmenu(event):
        menu = """
╔═══════════════════════════════════════════╗
║     🌊  𝐃𝐈𝐏𝐄𝐒𝐇𝐗𝐌𝐀𝐑𝐂𝐎 𝐅𝐋𝐎𝐖 𝐌𝐄𝐍𝐔  🌊     ║
╚═══════════════════════════════════════════╝

【 🌊 𝗙𝗟𝗢𝗪 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 】
  ✦ `.switch`           → toggle Flow Engine ON/OFF
  ✦ `.swipe <text>`     → swipe with custom text
  ✦ `.swipe`            → swipe using Dipesh & Marco DB texts
  ✦ `.stopswipe`        → stop swipe flood
  ✦ `.flowdelay <sec>`  → set delay between messages
  ✦ `.flowcount <n>`    → set number of messages per swipe
        """
        await event.reply(menu)

    @command("about")
    async def cmd_about(event):
        await event.reply(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "   👑  𝐀𝐁𝐎𝐔𝐓 𝐃𝐈𝐏𝐄𝐒𝐇𝐗𝐌𝐀𝐑𝐂𝐎  👑\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            " 🔹 **Version** : 7.0 (Glassmorphic Cloud Edition)\n"
            " 🔹 **Founders**: Dipesh & Marco\n"
            " 🔹 **Engine**  : Telethon + PTB + Flask Dynamic Web\n\n"
            " 🌟 **Highlights** :\n"
            " • Dual Dipesh & Marco Built-in Text Banks\n"
            " • Real-Time Web Control Panel with DB Sync\n"
            " • Advanced Security, Blitz & Domination Modes\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )

    # ------------------------- FLOW BOT -------------------------
    async def swipe_loop(chat, text):
        try:
            for _ in range(state.flow_count):
                if not state.flow_mode or "swipe" not in state.active_tasks: break
                try: await client.send_message(chat, text)
                except: pass
                await asyncio.sleep(state.flow_delay)
        except asyncio.CancelledError: pass
        finally: state.active_tasks.pop("swipe", None)

    @flow_command("swipe")
    async def cmd_swipe(event):
        args = event.raw_text.split(maxsplit=1)
        text = args[1] if len(args) > 1 else (random.choice(state.saved_texts) if state.saved_texts else random.choice(get_all_combined_texts()))
        if "swipe" in state.active_tasks: state.active_tasks["swipe"].cancel()
        state.active_tasks["swipe"] = asyncio.create_task(swipe_loop(event.chat, text))
        await event.reply(f"✅ **Dipeshxmarco Swipe** started! ({state.flow_count} msgs @ {state.flow_delay}s)")

    @flow_command("stopswipe")
    async def cmd_stopswipe(event):
        if "swipe" in state.active_tasks:
            state.active_tasks["swipe"].cancel()
            await event.reply("✅ Swipe stopped.")
        else: await event.reply("ℹ️ No active swipe.")

    @flow_command("flowdelay")
    async def cmd_flowdelay(event):
        try:
            val = float(event.raw_text.split(maxsplit=1)[1])
            if val < 0.05: return await event.reply("⚠️ Min 0.05s")
            state.flow_delay = val
            await event.reply(f"✅ Flow delay set to {state.flow_delay}s")
        except: await event.reply("⚠️ Invalid delay.")

    @flow_command("flowcount")
    async def cmd_flowcount(event):
        try:
            val = int(event.raw_text.split(maxsplit=1)[1])
            if val < 1: return await event.reply("⚠️ Min 1")
            state.flow_count = val
            await event.reply(f"✅ Flow count set to {state.flow_count}")
        except: await event.reply("⚠️ Invalid count.")

    # ------------------------- ADVANCED TOOLS (DIPESHXMARCO) -------------------------
    @command("sabchup")
    async def sabchup_cmd(event):
        state.auto_delete_chats[event.chat_id] = True
        await event.respond("🤐 **DIPESHXMARCO SABCHUP MODE ON** (0.05s auto-delete)")

    @command("speakall")
    async def speakall_cmd(event):
        state.auto_delete_chats.pop(event.chat_id, None)
        state.delete_target_users.pop(event.chat_id, None)
        state.delete_target_usernames.pop(event.chat_id, None)
        await event.respond("🗣️ **SPEAKALL - Auto-delete OFF**")

    @command("chup")
    async def chup_cmd(event):
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            uid = reply_msg.sender_id
            username = getattr(getattr(reply_msg, 'sender', None), 'username', None)
            state.delete_target_users[event.chat_id].add(uid)
            if username: state.delete_target_usernames[event.chat_id].add(username.lower())
            state.auto_delete_chats[event.chat_id] = True
            await event.respond("🤐 **CHUP!** Target locked by Dipeshxmarco.")
        else: await event.respond("Reply to a message with `.chup`")

    @command("bol")
    async def bol_cmd(event):
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            uid = reply_msg.sender_id
            if event.chat_id in state.delete_target_users: state.delete_target_users[event.chat_id].discard(uid)
            await event.respond("🗣️ **BOL!** Target released.")
        else: await event.respond("Reply to a message with `.bol`")

    @command("safe")
    async def safe_cmd(event):
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            state.safe_users.add(reply_msg.sender_id)
            return await event.respond("✅ **User added to Dipeshxmarco Safe List**")
        args = event.text.strip().split()[1:]
        for arg in args:
            try:
                ent = await client.get_entity(arg.lstrip('@'))
                state.safe_users.add(ent.id)
            except: pass
        await event.respond(f"🛡️ **Safe Users Count:** `{len(state.safe_users)}`")

    @command("namechange")
    async def namechange_cmd(event):
        args = event.text.strip().split()
        delay, mode = 0.1, "normal"
        if len(args) > 1:
            if args[1].lower() in ['time', 'emoji', 'owns', 'enters', 'dad']:
                mode = args[1].lower()
                if len(args) > 2:
                    try: delay = float(args[2]) / 1000
                    except: pass
            else:
                try: delay = float(args[1]) / 1000
                except: pass

        chat_id = event.chat_id
        chat = await event.get_chat()
        if not hasattr(chat, 'title'): return await event.respond("❌ **Groups only!**")

        state.namechange_active[chat_id] = True
        await event.respond(f"🔄 **DIPESHXMARCO NAME CHANGE ON** (`{mode}`)")

        async def namechange_task():
            original_title = chat.title
            counter = 0
            is_channel = hasattr(chat, 'megagroup') or hasattr(chat, 'broadcast')
            while state.namechange_active.get(chat_id):
                try:
                    curr_delay = state.namechange_delays.get(chat_id, delay)
                    tag = "DIPESH" if counter % 2 == 0 else "MARCO"
                    if mode == 'time': new_name = f"⏰ {datetime.now().strftime('%H:%M:%S')} ⚡ {tag} | {original_title}"
                    elif mode == 'emoji': new_name = f"{''.join(random.sample(RANDOM_EMOJIS, 3))} {original_title} {random.choice(COUNTRY_EMOJIS)}"
                    elif mode == 'owns': new_name = f"👑 DIPESHXMARCO OWNS {random.choice(RANDOM_EMOJIS)} {original_title}"
                    elif mode == 'enters': new_name = f"🚪 {tag} ENTERS {random.choice(RANDOM_EMOJIS)} {original_title} 🔥"
                    elif mode == 'dad': new_name = f"👑 {tag} RULES {random.choice(RANDOM_EMOJIS)} {original_title} 💀"
                    else: new_name = f"{random.choice(RANDOM_EMOJIS)} {original_title} • {tag} #{counter}"

                    if is_channel: await client(EditTitleRequest(channel=chat_id, title=new_name))
                    else: await client(EditChatTitleRequest(chat_id=chat_id, title=new_name))
                    counter += 1
                    await asyncio.sleep(curr_delay)
                except Exception:
                    await asyncio.sleep(1)
            state.namechange_active.pop(chat_id, None)

        state.active_tasks[f"nm_{chat_id}"] = asyncio.create_task(namechange_task())

    @command("stopnamechange")
    async def stopnamechange_cmd(event):
        if event.chat_id in state.namechange_active:
            state.namechange_active.pop(event.chat_id, None)
            task = state.active_tasks.pop(f"nm_{event.chat_id}", None)
            if task: task.cancel()
            await event.respond("✅ **DIPESHXMARCO NAME CHANGE STOPPED**")

    @command("lockname")
    async def lockname_cmd(event):
        chat = await event.get_chat()
        state.locked_titles[event.chat_id] = chat.title
        await event.respond(f"🔒 **NAME LOCKED BY DIPESHXMARCO:** `{chat.title}`")

    @command("lockchat")
    async def lockchat_cmd(event):
        state.locked_chat.add(event.chat_id)
        await event.respond("💬 **CHAT LOCKED BY DIPESHXMARCO**")

    @command("unlockchat")
    async def unlockchat_cmd(event):
        state.locked_chat.discard(event.chat_id)
        await event.respond("🔓 **CHAT UNLOCKED BY DIPESHXMARCO**")

    # ------------------------- FUN COMMANDS -------------------------
    @command("motivate")
    async def cmd_motivate(event): await event.reply(f"💪 **Motivation** : {random.choice(get_bank('motivation_quotes'))}")

    @command("truth")
    async def cmd_truth(event): await event.reply(f"🔮 **Truth** : {random.choice(get_bank('truths'))}")

    @command("dare")
    async def cmd_dare(event): await event.reply(f"⚡ **Dare** : {random.choice(get_bank('dares'))}")

    @command("shayari")
    async def cmd_shayari(event): await event.reply(f"💕 **Shayari** :\n{random.choice(get_bank('shayaris'))}")

    @command("joke")
    async def cmd_joke(event): await event.reply(f"😂 **Joke** : {random.choice(get_bank('jokes'))}")

    @command("quote")
    async def cmd_quote(event): await event.reply(f"📖 **Quote** : {random.choice(get_bank('quotes'))}")


# ════════════════════════════════════════════════════════════════════════════════
#   RUNNER MANAGER
# ════════════════════════════════════════════════════════════════════════════════
active_runtimes = {}

def _run_telethon_client(uid, slot, api_id, api_hash, session_string):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        client = TelegramClient(StringSession(session_string), int(api_id), api_hash, loop=loop)
        register_userbot_engine(client, int(uid))
        loop.run_until_complete(client.connect())
        if not loop.run_until_complete(client.is_user_authorized()):
            logger.warning(f"Userbot {uid}:{slot} is not authorized.")
            return

        active_runtimes[(str(uid), str(slot))] = {
            "client": client,
            "loop": loop,
            "start_time": time.time()
        }
        logger.info(f"Dipeshxmarco Userbot started for user {uid} (slot {slot})")
        loop.run_until_complete(client.run_until_disconnected())
    except Exception as e:
        logger.error(f"Userbot thread error: {e}")
    finally:
        active_runtimes.pop((str(uid), str(slot)), None)

class RunnerManager:
    def is_running(self, uid, slot):
        return (str(uid), str(slot)) in active_runtimes

    def get_uptime(self, uid, slot):
        key = (str(uid), str(slot))
        if key in active_runtimes:
            e = int(time.time() - active_runtimes[key]["start_time"])
            h, r = divmod(e, 3600); m, s = divmod(r, 60)
            return f"{h}h {m}m {s}s"
        return "Stopped"

    def running_count(self):
        return len(active_runtimes)

    def start_userbot(self, uid, slot, api_id, api_hash, session_string, uid_str):
        key = (str(uid), str(slot))
        if key in active_runtimes:
            return True
        try:
            t = threading.Thread(
                target=_run_telethon_client,
                args=(uid, slot, api_id, api_hash, session_string),
                daemon=True
            )
            t.start()
            time.sleep(0.8)
            return True
        except Exception as e:
            logger.error(f"Failed to start thread: {e}")
            return False

    def stop_userbot(self, uid, slot):
        key = (str(uid), str(slot))
        if key in active_runtimes:
            try:
                loop = active_runtimes[key]["loop"]
                client = active_runtimes[key]["client"]
                asyncio.run_coroutine_threadsafe(client.disconnect(), loop)
            except Exception:
                pass
            active_runtimes.pop(key, None)
        return True

    def restart_userbot(self, uid, slot, api_id, api_hash, session_string, uid_str):
        self.stop_userbot(uid, slot)
        time.sleep(0.8)
        return self.start_userbot(uid, slot, api_id, api_hash, session_string, uid_str)

    def stop_all_for_user(self, uid):
        slots_to_stop = [s for (u, s) in list(active_runtimes.keys()) if u == str(uid)]
        for slot in slots_to_stop:
            self.stop_userbot(uid, slot)

runner = RunnerManager()

# ════════════════════════════════════════════════════════════════════════════════
#   UNICODE FONT HELPERS
# ════════════════════════════════════════════════════════════════════════════════
def bold_serif(t: str) -> str:
    return "".join(
        chr(ord(c) - ord('A') + 0x1D400) if 'A' <= c <= 'Z' else
        chr(ord(c) - ord('a') + 0x1D41A) if 'a' <= c <= 'z' else
        chr(ord(c) - ord('0') + 0x1D7CE) if '0' <= c <= '9' else c
        for c in t
    )

def sans_bold(t: str) -> str:
    return "".join(
        chr(ord(c) - ord('A') + 0x1D5D4) if 'A' <= c <= 'Z' else
        chr(ord(c) - ord('a') + 0x1D5EE) if 'a' <= c <= 'z' else
        chr(ord(c) - ord('0') + 0x1D7EC) if '0' <= c <= '9' else c
        for c in t
    )

def mono(t: str) -> str:
    return f"`{t}`"

DIV = "━━━━━━━━━━━━━━━━━━━━━━━━━━"
TOP = "╔══════════════════════════╗"
BOT = "╚══════════════════════════╝"

def is_owner(uid): return int(uid) == int(OWNER_ID)
def is_premium(uid): return is_owner(uid) or db.is_sudo(uid, OWNER_ID)

def uptime_str():
    e = int(time.time() - START_TIME)
    h, r = divmod(e, 3600); m, s = divmod(r, 60)
    return f"{h}h {m}m {s}s"

def _phone_label(acct: dict) -> str:
    phone = acct.get("phone", "")
    return phone if phone else f"Account #{acct.get('slot', 0) + 1}"

async def check_blocked(update: Update) -> bool:
    if db.is_blocked(update.effective_user.id):
        await update.message.reply_text("🚫 **You are blocked from Dipeshxmarco Hoster.**", parse_mode=ParseMode.MARKDOWN)
        return False
    return True

async def cleanup_pending(uid: int):
    data = pending_logins.pop(uid, None)
    if data and data.get("client"):
        try: await data["client"].disconnect()
        except: pass

# ════════════════════════════════════════════════════════════════════════════════
#   TELEGRAM HOSTER BOT HANDLERS
# ════════════════════════════════════════════════════════════════════════════════
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_blocked(update): return
    uid  = update.effective_user.id
    name = update.effective_user.first_name or "User"

    if not db.user_exists(uid):
        db.save_user_meta(uid, {"first_name": name, "joined_at": int(time.time())})

    accounts = db.get_accounts(uid)
    hosted   = [a for a in accounts if a.get("hosted")]
    running  = [a for a in hosted if runner.is_running(uid, a["slot"])]

    status_line = f"📱 Accounts: `{len(hosted)}` hosted | `{len(running)}` running" if hosted else "⚪ Userbot: `Not hosted yet`"

    keyboard = [
        [InlineKeyboardButton("🚀  𝗛𝗼𝘀𝘁 𝗠𝘆 𝗨𝘀𝗲𝗿𝗯𝗼𝘁", callback_data="host")],
        [
            InlineKeyboardButton("📋  𝗠𝗮𝘀𝘁𝗲𝗿 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀", callback_data="commands"),
            InlineKeyboardButton("🌊  𝗙𝗹𝗼𝘄 𝗠𝗲𝗻𝘂", callback_data="flow_menu"),
        ],
        [
            InlineKeyboardButton("📊  𝗦𝘁𝗮𝘁𝘂𝘀", callback_data="status"),
            InlineKeyboardButton("🗑️  𝗟𝗼𝗴𝗼𝘂𝘁", callback_data="menu_logout"),
        ],
        [
            InlineKeyboardButton("📞  𝗦𝘂𝗽𝗽𝗼𝗿𝘁", callback_data="support"),
            InlineKeyboardButton("❓  𝗛𝗲𝗹𝗽 & 𝗚𝘂𝗶𝗱𝗲", callback_data="help"),
        ],
    ]

    text = (
        f"👑 **DIPESHXMARCO ULTIMATE ARCHITECTURE** 👑\n"
        f"{DIV}\n"
        f"✨ Welcome back, **{name}**!\n\n"
        f"» **Engine:** `v7.0-DIPESHXMARCO-CLOUD`\n"
        f"» **Status:** `ONLINE & SECURE`\n"
        f"» **Your ID:** `{uid}`\n"
        f"» {status_line}\n\n"
        f"👇 Select an option below or use the **Dipeshxmarco Web Dashboard**:"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard))

async def cmd_host_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = update.callback_query.message.reply_text if update.callback_query else update.message.reply_text
    if update.callback_query: await update.callback_query.answer()
    if not await check_blocked(update): return ConversationHandler.END
    uid = update.effective_user.id

    accounts = [a for a in db.get_accounts(uid) if a.get("hosted")]
    if len(accounts) >= MAX_ACCOUNTS_PER_USER:
        await reply(f"📱 **Account Limit Reached ({len(accounts)}/{MAX_ACCOUNTS_PER_USER})**\nUse `/logout` first.", parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

    await cleanup_pending(uid)
    await reply(
        f"{TOP}\n║ 🚀 **Dipeshxmarco Deploy** 🚀 ║\n{BOT}\n\n"
        f"📱 **Step 1 of 3:** Enter your Telegram Phone Number\n"
        f"🌍 Format: `+91XXXXXXXXXX`\n\n"
        f"🔴 Send `/cancel` to abort",
        parse_mode=ParseMode.MARKDOWN,
    )
    return ASK_PHONE

async def host_got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid   = update.effective_user.id
    phone = update.message.text.strip()
    msg   = await update.message.reply_text("⏳ **Sending OTP via Dipeshxmarco Engine...** 📨", parse_mode=ParseMode.MARKDOWN)
    try:
        client = TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await client.connect()
        result = await client.send_code_request(phone)
        pending_logins[uid] = {"client": client, "phone": phone, "phone_code_hash": result.phone_code_hash}
        await msg.edit_text(
            f"📨 **OTP Sent Successfully!**\n\n"
            f"📱 Number: `{phone}`\n"
            f"📩 **Step 2 of 3:** Send the OTP with spaces (e.g. `1 2 3 4 5`)",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ASK_CODE
    except Exception as e:
        await cleanup_pending(uid)
        await msg.edit_text(f"❌ **Error:** `{str(e)[:120]}`\nTry `/host` again.", parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

async def host_got_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    code = update.message.text.strip().replace(" ", "")
    pending = pending_logins.get(uid)
    if not pending:
        await update.message.reply_text("❌ Session expired. Send `/host` again.")
        return ConversationHandler.END

    client: TelegramClient = pending["client"]
    phone = pending["phone"]
    hash_ = pending["phone_code_hash"]
    msg = await update.message.reply_text("🔐 **Verifying OTP...**", parse_mode=ParseMode.MARKDOWN)
    try:
        await client.sign_in(phone, code, phone_code_hash=hash_)
        session_string = client.session.save()
        await client.disconnect()
        pending_logins.pop(uid, None)
        await _deploy_userbot(update, context, uid, session_string, phone, msg)
        return ConversationHandler.END
    except SessionPasswordNeededError:
        await msg.edit_text("🔒 **2FA Detected!**\n**Step 3 of 3:** Enter your 2FA Password:", parse_mode=ParseMode.MARKDOWN)
        return ASK_2FA
    except Exception as e:
        await cleanup_pending(uid)
        await msg.edit_text(f"❌ **Error:** `{str(e)[:120]}`", parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

async def host_got_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid      = update.effective_user.id
    password = update.message.text.strip()
    pending  = pending_logins.get(uid)
    if not pending:
        await update.message.reply_text("❌ Session expired. Send `/host` again.")
        return ConversationHandler.END

    client: TelegramClient = pending["client"]
    phone = pending.get("phone", "")
    msg = await update.message.reply_text("🔐 **Verifying 2FA Password...**", parse_mode=ParseMode.MARKDOWN)
    try:
        await client.sign_in(password=password)
        session_string = client.session.save()
        await client.disconnect()
        pending_logins.pop(uid, None)
        await _deploy_userbot(update, context, uid, session_string, phone, msg)
        return ConversationHandler.END
    except Exception as e:
        await cleanup_pending(uid)
        await msg.edit_text(f"❌ **Wrong 2FA Password:** `{str(e)[:120]}`", parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END

async def _deploy_userbot(update, context, uid, session_string, phone, msg):
    name     = update.effective_user.first_name or "User"
    accounts = db.get_accounts(uid)
    existing = {a.get("slot") for a in accounts}
    slot = 0
    while slot in existing: slot += 1

    ok = runner.start_userbot(uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, session_string, str(uid))
    if ok:
        db.save_user_meta(uid, {"first_name": name})
        db.add_account(uid, {
            "slot": slot,
            "session_string": session_string,
            "hosted": True,
            "hosted_at": int(time.time()),
            "phone": phone,
        })
        await msg.edit_text(
            f"🎉 **Dipeshxmarco Deploy Successful!** 🎉\n\n"
            f"✅ **Slot:** `#{slot+1}`\n"
            f"📱 **Phone:** `{phone}`\n"
            f"⚡ **Engine:** `v7.0-DIPESHXMARCO`\n\n"
            f"Type `.alive` or `.menu` in any chat!",
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        await msg.edit_text(f"❌ **Deploy Failed.** Contact {SUPPORT_USERNAME}", parse_mode=ParseMode.MARKDOWN)

async def host_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cleanup_pending(update.effective_user.id)
    await update.message.reply_text("🚫 Login Cancelled.")
    return ConversationHandler.END

async def cmd_myaccounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    hosted = [a for a in db.get_accounts(uid) if a.get("hosted")]
    if not hosted:
        await update.message.reply_text("📱 No accounts hosted yet. Send `/host` to deploy!")
        return
    lines, kb = [], []
    for acct in hosted:
        slot = acct["slot"]
        alive = runner.is_running(uid, slot)
        icon = "🟢" if alive else "🔴"
        lines.append(f"{icon} **Account #{slot+1}** — `{_phone_label(acct)}` ({runner.get_uptime(uid, slot)})")
        kb.append([
            InlineKeyboardButton(f"🔄 Restart #{slot+1}", callback_data=f"restart_acc_{slot}"),
            InlineKeyboardButton(f"🗑️ Logout #{slot+1}", callback_data=f"confirm_logout_{slot}")
        ])
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(kb))

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_myaccounts(update, context)

async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_myaccounts(update, context)

async def cmd_logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_myaccounts(update, context)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = update.effective_user.id
    data = query.data

    if data == "commands":
        await query.message.reply_text("👑 **Dipeshxmarco Master Menu:** Send `.menu` from your hosted Userbot in any chat!", parse_mode=ParseMode.MARKDOWN)
    elif data == "flow_menu":
        await query.message.reply_text("🌊 **Dipeshxmarco Flow Menu:** Send `.switch` and `.flowmenu` from your Userbot!", parse_mode=ParseMode.MARKDOWN)
    elif data == "status" or data == "menu_logout":
        await cmd_myaccounts(update, context)
    elif data == "support":
        await query.message.reply_text(f"📞 **Support:** {SUPPORT_USERNAME}")
    elif data == "help":
        await query.message.reply_text("📖 **Guide:** Tap `/host`, enter phone & OTP, then use `.menu`, `.raid`, `.reply`, `.swipe` in any chat!")
    elif data.startswith("restart_acc_"):
        slot = int(data.split("_")[-1])
        acct = db.get_account(uid, slot)
        if acct:
            runner.restart_userbot(uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, acct["session_string"], str(uid))
            await query.message.reply_text(f"✅ **Account #{slot+1} Restarted!**", parse_mode=ParseMode.MARKDOWN)
    elif data.startswith("confirm_logout_"):
        slot = int(data.split("_")[-1])
        runner.stop_userbot(uid, slot)
        db.remove_account(uid, slot)
        await query.message.edit_text(f"🗑️ **Account #{slot+1} Logged Out.**", parse_mode=ParseMode.MARKDOWN)


# ════════════════════════════════════════════════════════════════════════════════
#   FLASK DYNAMIC WEB CONTROL PANEL & REST API
# ════════════════════════════════════════════════════════════════════════════════
web_app = Flask(__name__, template_folder="templates", static_folder="static")
web_loop = asyncio.new_event_loop()
threading.Thread(target=web_loop.run_forever, daemon=True).start()

def check_web_auth(req):
    key = req.headers.get("X-Admin-Key") or req.args.get("key") or (req.json or {}).get("key")
    return key == WEB_ADMIN_KEY

@web_app.route("/")
def index():
    return render_template("index.html")

@web_app.route("/api/overview", methods=["GET"])
def api_overview():
    accounts_list = []
    for uid_str, slots in db.data.get("accounts", {}).items():
        user_meta = db.data.get("users", {}).get(uid_str, {})
        for slot_str, acc in slots.items():
            if acc.get("hosted"):
                alive = runner.is_running(uid_str, slot_str)
                accounts_list.append({
                    "uid": uid_str,
                    "name": user_meta.get("first_name", f"User {uid_str}"),
                    "slot": int(slot_str),
                    "phone": acc.get("phone", "N/A"),
                    "running": alive,
                    "uptime": runner.get_uptime(uid_str, slot_str)
                })

    text_counts = {k: len(v) for k, v in db.get_all_text_banks().items()}
    return jsonify({
        "engine": "Dipeshxmarco v7.0 Ultimate",
        "bot_on": db.is_bot_on(),
        "uptime": uptime_str(),
        "total_users": db.user_count(),
        "hosted_count": db.hosted_count(),
        "running_count": runner.running_count(),
        "max_slots": MAX_USERBOTS,
        "sudo_users": db.get_sudo_users(),
        "blocked_users": db.get_blocked(),
        "accounts": accounts_list,
        "text_counts": text_counts,
        "total_texts": sum(text_counts.values())
    })

@web_app.route("/api/texts", methods=["GET"])
def api_get_texts():
    category = request.args.get("category", "RAID_TEXTS")
    return jsonify({
        "category": category,
        "categories": list(db.get_all_text_banks().keys()),
        "texts": db.get_text_bank(category)
    })

@web_app.route("/api/texts/add", methods=["POST"])
def api_add_text():
    if not check_web_auth(request): return jsonify({"error": "Invalid Admin Key"}), 403
    data = request.json or {}
    cat = data.get("category", "RAID_TEXTS")
    txt = (data.get("text") or "").strip()
    if not txt: return jsonify({"error": "Empty text"}), 400
    db.add_bank_text(cat, txt)
    return jsonify({"ok": True, "texts": db.get_text_bank(cat)})

@web_app.route("/api/texts/delete", methods=["POST"])
def api_del_text():
    if not check_web_auth(request): return jsonify({"error": "Invalid Admin Key"}), 403
    data = request.json or {}
    cat = data.get("category", "RAID_TEXTS")
    idx = int(data.get("index", -1))
    db.delete_bank_text(cat, idx)
    return jsonify({"ok": True, "texts": db.get_text_bank(cat)})

@web_app.route("/api/account/action", methods=["POST"])
def api_account_action():
    if not check_web_auth(request): return jsonify({"error": "Invalid Admin Key"}), 403
    data = request.json or {}
    uid = str(data.get("uid"))
    slot = int(data.get("slot", 0))
    action = data.get("action")
    acct = db.get_account(uid, slot)
    if not acct: return jsonify({"error": "Account not found"}), 404

    if action == "start":
        runner.start_userbot(uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, acct["session_string"], uid)
    elif action == "stop":
        runner.stop_userbot(uid, slot)
    elif action == "restart":
        runner.restart_userbot(uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, acct["session_string"], uid)
    elif action == "delete":
        runner.stop_userbot(uid, slot)
        db.remove_account(uid, slot)
    return jsonify({"ok": True})

@web_app.route("/api/system/action", methods=["POST"])
def api_system_action():
    if not check_web_auth(request): return jsonify({"error": "Invalid Admin Key"}), 403
    data = request.json or {}
    action = data.get("action")

    if action == "toggle_bot":
        curr = db.is_bot_on()
        db.set_bot_settings({"is_on": not curr})
    elif action == "restart_all":
        for uid_str in db.get_all_users():
            for acct in db.get_accounts(uid_str):
                if acct.get("hosted") and acct.get("session_string"):
                    runner.restart_userbot(uid_str, acct["slot"], str(TELEGRAM_API_ID), TELEGRAM_API_HASH, acct["session_string"], uid_str)
    elif action == "add_sudo":
        db.add_sudo(int(data.get("target_uid")))
    elif action == "del_sudo":
        db.remove_sudo(int(data.get("target_uid")))
    elif action == "block_user":
        target = int(data.get("target_uid"))
        db.block_user(target)
        runner.stop_all_for_user(target)
    elif action == "unblock_user":
        db.unblock_user(int(data.get("target_uid")))
    elif action == "reset_texts":
        db.reset_text_banks()

    return jsonify({"ok": True})

# --- WEB OTP HOSTING ENDPOINTS ---
@web_app.route("/api/webhost/send_code", methods=["POST"])
def api_webhost_send_code():
    data = request.json or {}
    phone = (data.get("phone") or "").strip()
    uid = str(data.get("uid") or OWNER_ID).strip()
    if not phone: return jsonify({"error": "Phone number required"}), 400

    async def _send():
        client = TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        await client.connect()
        res = await client.send_code_request(phone)
        web_pending_logins[phone] = {"client": client, "phone_code_hash": res.phone_code_hash, "uid": uid}

    try:
        fut = asyncio.run_coroutine_threadsafe(_send(), web_loop)
        fut.result(timeout=20)
        return jsonify({"ok": True, "message": "OTP sent to Telegram!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@web_app.route("/api/webhost/verify_code", methods=["POST"])
def api_webhost_verify_code():
    data = request.json or {}
    phone = (data.get("phone") or "").strip()
    code = (data.get("code") or "").strip().replace(" ", "")
    password = (data.get("password") or "").strip()
    pending = web_pending_logins.get(phone)
    if not pending: return jsonify({"error": "Session expired. Send OTP again."}), 400

    async def _verify():
        client = pending["client"]
        try:
            if password:
                await client.sign_in(password=password)
            else:
                await client.sign_in(phone, code, phone_code_hash=pending["phone_code_hash"])
            session_str = client.session.save()
            await client.disconnect()
            return {"ok": True, "session": session_str}
        except SessionPasswordNeededError:
            return {"need_2fa": True}

    try:
        fut = asyncio.run_coroutine_threadsafe(_verify(), web_loop)
        res = fut.result(timeout=20)
        if res.get("need_2fa"):
            return jsonify({"need_2fa": True, "message": "2FA Password Required"})

        session_string = res["session"]
        uid = pending["uid"]
        web_pending_logins.pop(phone, None)

        accounts = db.get_accounts(uid)
        existing = {a.get("slot") for a in accounts}
        slot = 0
        while slot in existing: slot += 1

        runner.start_userbot(uid, slot, str(TELEGRAM_API_ID), TELEGRAM_API_HASH, session_string, str(uid))
        db.save_user_meta(uid, {"first_name": f"WebUser-{uid[-4:]}"})
        db.add_account(uid, {
            "slot": slot,
            "session_string": session_string,
            "hosted": True,
            "hosted_at": int(time.time()),
            "phone": phone,
        })
        return jsonify({"ok": True, "slot": slot + 1})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def run_flask_server():
    logger.info(f"🌐 Starting Dipeshxmarco Dynamic Web Panel on port {PORT}...")
    web_app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


# ════════════════════════════════════════════════════════════════════════════════
#   STARTUP & MAIN
# ════════════════════════════════════════════════════════════════════════════════
async def auto_health_check(context: ContextTypes.DEFAULT_TYPE):
    if not db.is_bot_on(): return
    for uid_str in db.get_all_users():
        if db.is_blocked(int(uid_str)): continue
        for acct in db.get_accounts(uid_str):
            if acct.get("hosted") and acct.get("session_string"):
                if not runner.is_running(uid_str, acct["slot"]):
                    runner.start_userbot(uid_str, acct["slot"], str(TELEGRAM_API_ID), TELEGRAM_API_HASH, acct["session_string"], uid_str)

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start",      "Dipeshxmarco Welcome"),
        BotCommand("host",       "Add & Deploy Account"),
        BotCommand("myaccounts", "Manage All Accounts"),
        BotCommand("status",     "Check Userbot Status"),
        BotCommand("restart",    "Restart Userbot"),
        BotCommand("logout",     "Logout an Account"),
    ])
    if db.is_bot_on():
        count = 0
        for uid_str in db.get_all_users():
            if db.is_blocked(int(uid_str)): continue
            for acct in db.get_accounts(uid_str):
                if acct.get("hosted") and acct.get("session_string"):
                    ok = runner.start_userbot(uid_str, acct["slot"], str(TELEGRAM_API_ID), TELEGRAM_API_HASH, acct["session_string"], uid_str)
                    if ok: count += 1
        logger.info(f"[STARTUP] Auto-started {count} Dipeshxmarco userbots.")

def main():
    # Start Flask Web Dashboard in background thread for Render
    threading.Thread(target=run_flask_server, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    host_conv = ConversationHandler(
        entry_points=[
            CommandHandler("host", cmd_host_start),
            CallbackQueryHandler(cmd_host_start, pattern="^host$"),
        ],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_phone)],
            ASK_CODE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_code)],
            ASK_2FA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, host_got_2fa)],
        },
        fallbacks=[CommandHandler("cancel", host_cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(host_conv)
    app.add_handler(CommandHandler("myaccounts", cmd_myaccounts))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("restart", cmd_restart))
    app.add_handler(CommandHandler("logout", cmd_logout))
    app.add_handler(CallbackQueryHandler(callback_handler))

    if app.job_queue:
        app.job_queue.run_repeating(auto_health_check, interval=300, first=60)

    logger.info("👑 Dipeshxmarco Hoster Bot + Web Dashboard STARTED!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
