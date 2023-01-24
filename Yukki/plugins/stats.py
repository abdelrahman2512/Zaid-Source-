import os 
import time
import platform, socket, re, uuid, json, psutil, logging

from pymongo import MongoClient
from ..config import MONGO_DB_URI as smex

from pyrogram.types import Message
from pyrogram import filters, Client
from pyrogram import __version__ as pyrover
from pytgcalls import (__version__ as pytover)
from sys import version as pyver

from Yukki import app, SUDOERS, BOT_ID, __version__ as yukki_version, YUKKI_START_TIME
from Yukki.YukkiUtilities.database.sudo import (get_sudoers, get_sudoers, remove_sudo)
from Yukki.YukkiUtilities.database.playlist import get_playlist_count
from Yukki.YukkiUtilities.database.gbanned import get_gbans_count
from Yukki.YukkiUtilities.database.chats import get_served_chats
from ..YukkiUtilities.helpers.time import get_readable_time
from ..YukkiUtilities.helpers.filters import command


@app.on_message(filters.command("الاحصائيات", [".", ""]) & filters.user(SUDOERS))
async def get_statistic(_, message):
    m = await message.reply_text("🔄 **Getting bot stats...**")
    served_chats = []
    chats = await get_served_chats()
    for chat in chats:
        served_chats.append(int(chat["chat_id"]))
    blocked = await get_gbans_count()
    sudoers = await get_sudoers()
    j = 0
    for count, user_id in enumerate(sudoers, 0):
        try:                     
            user = await app.get_users(user_id)
            j += 1
        except Exception:
            continue                     
    modules_count ="20"
    sc = platform.system()
    arch = platform.machine()
    ram = str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
    bot_uptime = int(time.time() - YUKKI_START_TIME)
    uptime = f"{get_readable_time((bot_uptime))}"
    hdd = psutil.disk_usage('/')
    total = (hdd.total / (1024.0 ** 3))
    total = str(total)
    used = (hdd.used / (1024.0 ** 3))
    used = str(used)
    free = (hdd.free / (1024.0 ** 3))
    free = str(free)
    msg = f"""
✶ **الاحصائيات الحالية:**

• **Bot Stats:**

**المحظورين عام:** `{blocked}`
**المطورين** `{j}`
**الدردشات:** `{len(served_chats)}`
"""
    served_chats.pop(0)
    await m.edit(msg, disable_web_page_preview=True)
