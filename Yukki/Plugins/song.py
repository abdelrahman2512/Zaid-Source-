import os
import time
import requests
import wget
import random
import shutil
import yt_dlp
import psutil
import asyncio
import subprocess

from os import path
from typing import Union
from pytube import YouTube
from yt_dlp import YoutubeDL
from asyncio import QueueEmpty
from sys import version as pyver
from youtubesearchpython import VideosSearch
from youtube_search import YoutubeSearch

from pyrogram import Client, filters
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import (
    Message,
    Audio,
    Voice,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

from .. import converter
from ..config import DURATION_LIMIT
from Yukki import dbb, app, BOT_USERNAME, BOT_ID, ASSID, ASSNAME, ASSUSERNAME, ASSMENTION
from Yukki.YukkiUtilities.database.chats import (get_served_chats, is_served_chat, add_served_chat, get_served_chats)
from ..YukkiUtilities.helpers.inline import (play_keyboard, search_markup, play_markup, playlist_markup, audio_markup, play_list_keyboard)
from ..YukkiUtilities.helpers.decorators import errors
from ..YukkiUtilities.helpers.filters import command
from ..YukkiUtilities.helpers.gets import (get_url, themes, random_assistant, ass_det)
from ..YukkiUtilities.helpers.logger import LOG_CHAT
from ..YukkiUtilities.helpers.thumbnails import down_thumb
from ..YukkiUtilities.helpers.ytdl import ytdl_opts 



flex = {}
chat_watcher_group = 3

def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":")))
    )


@Client.on_message(filters.command("/search", [".", ""]) & ~filters.edited)
async def musicdl(_, message: Message):
    await message.delete()
    chat_id = message.chat.id
    if message.sender_chat:
        return await message.reply_text("✶ يرجى الطلب من حساب شخصي")  
    user_id = message.from_user.id
    chat_title = message.chat.title
    username = message.from_user.first_name
    checking = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"
    url = get_url(message)
    fucksemx = 0
    if url:
        query = " ".join(message.command[1:])
        mystic = await _.send_message(chat_id, "✶ **جار البحث...**")
        ydl_opts = {"format": "bestaudio/best"}
        try:
            results = VideosSearch(query, limit=1)
            for result in results.result()["result"]:
                title = (result["title"])
                duration = (result["duration"])
                views = (result["viewCount"]["short"])  
                thumbnail = (result["thumbnails"][0]["url"])
                link = (result["link"])
                idxz = (result["id"])
                videoid = (result["id"])
        except Exception as e:
            return await mystic.edit_text("**✶ لم يتم العثور على نتائج**")    
        smex = int(time_to_seconds(duration))
        if smex > DURATION_LIMIT:
            return await mystic.edit_text(f"**✶ المدة المسموح بها:  {DURATION_LIMIT} دقيقة\n✶ المدة المطلوبة : {duration} دقيقة**")
        if duration == "None":
            return await mystic.edit_text("❌ **live stream not supported**")
        if views == "None":
            return await mystic.edit_text("❌ **live stream not supported**")
        thumb = await down_thumb(thumbnail, user_id)
        buttons = gets(videoid, user_id)
        m = await message.reply_photo(
            photo=thumb,
            reply_markup=InlineKeyboardMarkup(buttons),    
            caption=(f"✶ <b>الأسم:</b> [{title[:65]}]({url})\n\n✶ [مزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{id})")
        )   
        os.remove(thumb)
    else:
        if len(message.command) < 2:
            await message.reply_text("**✶ اكتب ✶ بحث + اسم الاغنية **")
        query = " ".join(message.command[1:])
        mystic = await _.send_message(chat_id, "✶ **جار البحث...**")
        try:
            a = VideosSearch(query, limit=5)
            result = (a.result()).get("result")
            title1 = (result[0]["title"])
            duration1 = (result[0]["duration"])
            title2 = (result[1]["title"])
            duration2 = (result[1]["duration"])      
            title3 = (result[2]["title"])
            duration3 = (result[2]["duration"])
            title4 = (result[3]["title"])
            duration4 = (result[3]["duration"])
            title5 = (result[4]["title"])
            duration5 = (result[4]["duration"])
            ID1 = (result[0]["id"])
            ID2 = (result[1]["id"])
            ID3 = (result[2]["id"])
            ID4 = (result[3]["id"])
            ID5 = (result[4]["id"])
        except Exception as e:
            return await mystic.edit_text("**✶ لم يتم العثور على نتائج**")
        thumb ="https://telegra.ph/file/137b088be8f4f65c47a89.jpg"
        link = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        await mystic.edit(
            f"✶ اختر من النتائج لاقوم بتحميله !\n\n𝟏 <b>[{title1[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID1})\n\n𝟐 <b>[{title2[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID2})\n\n𝟑 <b>[{title3[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID3})\n\n𝟒 <b>[{title4[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID4})\n\n𝟓 <b>[{title5[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID5})",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return
    
    
@Client.on_callback_query(filters.regex(pattern=r"beta"))
async def download_data(_,CallbackQuery): 
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    chat_title = CallbackQuery.message.chat.title
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id 
    try:
        id,duration,user_id = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"✶ حدث خطأ")
    if duration == "None":
        return await CallbackQuery.message.reply_text(f"❌ **live stream not supported**")      
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer("✶ sorry this is not your request", show_alert=True)
    await CallbackQuery.message.delete()
    checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
    url = (f"https://www.youtube.com/watch?v={id}")
    videoid = id
    idx = id
    smex = int(time_to_seconds(duration))
    if smex > DURATION_LIMIT:
        await CallbackQuery.message.reply_text(f"**✶ المدة المسموح بها:  {DURATION_LIMIT} دقيقة\n✶ المدة المطلوبة : {duration} دقيقة**")
        return 
    try:
        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
            x = ytdl.extract_info(url, download=False)
    except Exception as e:
        return await CallbackQuery.message.reply_text(f"failed to download this video.\n\n**reason:** `{e}`") 
    title = (x["title"])
    thumbnail = (x["thumbnail"])
    idx = (x["id"])
    videoid = (x["id"])
    thumb = await down_thumb(thumbnail, user_id)
    buttons = gets(videoid, user_id)
    m = await CallbackQuery.message.reply_photo(
        photo=thumb,
        reply_markup=InlineKeyboardMarkup(buttons),    
        caption=(f"✶ **الأسم:** [{title[:80]}]({url})\n\n✶ [مزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{id})")
    )   
    os.remove(thumb)
    await CallbackQuery.message.delete()
        
        
@Client.on_callback_query(filters.regex(pattern=r"chonga"))
async def chonga(_,CallbackQuery): 
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    print(callback_request)
    userid = CallbackQuery.from_user.id 
    try:
        id , query, user_id = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"✶ حدث خطأ")       
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer("✶ ليس طلبك", show_alert=True)
    i=int(id)
    query = str(query)
    try:
        a = VideosSearch(query, limit=10)
        result = (a.result()).get("result")
        title1 = (result[0]["title"])
        duration1 = (result[0]["duration"])
        title2 = (result[1]["title"])
        duration2 = (result[1]["duration"])      
        title3 = (result[2]["title"])
        duration3 = (result[2]["duration"])
        title4 = (result[3]["title"])
        duration4 = (result[3]["duration"])
        title5 = (result[4]["title"])
        duration5 = (result[4]["duration"])
        title6 = (result[5]["title"])
        duration6 = (result[5]["duration"])
        title7= (result[6]["title"])
        duration7 = (result[6]["duration"])      
        title8 = (result[7]["title"])
        duration8 = (result[7]["duration"])
        title9 = (result[8]["title"])
        duration9 = (result[8]["duration"])
        title10 = (result[9]["title"])
        duration10 = (result[9]["duration"])
        ID1 = (result[0]["id"])
        ID2 = (result[1]["id"])
        ID3 = (result[2]["id"])
        ID4 = (result[3]["id"])
        ID5 = (result[4]["id"])
        ID6 = (result[5]["id"])
        ID7 = (result[6]["id"])
        ID8 = (result[7]["id"])
        ID9 = (result[8]["id"])
        ID10 = (result[9]["id"])                    
    except Exception as e:
        return await mystic.edit_text(f"song not found.\n**reason:** {e}")
    if i == 1:
        link = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup2(ID6, ID7, ID8, ID9, ID10, duration6, duration7, duration8, duration9, duration10 ,user_id, query)
        await CallbackQuery.edit_message_text(
            f"✶ اختر من النتائج لاقوم بالتحميل !\n\n𝟔 <b>[{title6[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID6})\n\n𝟕 <b>[{title7[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID7})\n\n𝟖 <b>[{title8[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID8})\n\n𝟗 <b>[{title9[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID9})\n\n𝟏𝟎 <b>[{title10[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID10})",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return    
    if i == 2:
        link = "https://www.youtube.com/watch?v={id}"
        buttons = search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query)
        await CallbackQuery.edit_message_text(
            f"✶ اختر من النتائج لاقوم بالتحميل !\n\n𝟏 <b>[{title1[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID1})\n\n𝟐 <b>[{title2[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID2})\n\n𝟑 <b>[{title3[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID3})\n\n𝟒 <b>[{title4[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID4})\n\n𝟓 <b>[{title5[:100]}...]({link})</b>\n └ ✶ [المزيد من المعلومات](https://t.me/{BOT_USERNAME}?start=info_{ID5})",    
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
        return    
      

def search_markup(ID1, ID2, ID3, ID4, ID5, duration1, duration2, duration3, duration4, duration5, user_id, query):
    buttons= [
            [
                InlineKeyboardButton(text="𝟏", callback_data=f'beta {ID1}|{duration1}|{user_id}'),
                InlineKeyboardButton(text="𝟐", callback_data=f'beta {ID2}|{duration2}|{user_id}'),
                InlineKeyboardButton(text="𝟑", callback_data=f'beta {ID3}|{duration3}|{user_id}')
            ],
            [ 
                InlineKeyboardButton(text="𝟒", callback_data=f'beta {ID4}|{duration4}|{user_id}'),
                InlineKeyboardButton(text="𝟓", callback_data=f'beta {ID5}|{duration5}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="التالي", callback_data=f'chonga 1|{query}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="اغلاق", callback_data=f"ppcl2 smex|{user_id}")
            ],
        ]
    return buttons   

def search_markup2(ID6, ID7, ID8, ID9, ID10, duration6, duration7, duration8, duration9, duration10 ,user_id, query):
    buttons= [
            [
                InlineKeyboardButton(text="𝟔", callback_data=f'beta {ID6}|{duration6}|{user_id}'),
                InlineKeyboardButton(text="𝟕", callback_data=f'beta {ID7}|{duration7}|{user_id}'),
                InlineKeyboardButton(text="𝟖", callback_data=f'beta {ID8}|{duration8}|{user_id}')
            ],
            [ 
                InlineKeyboardButton(text="𝟗", callback_data=f'beta {ID9}|{duration9}|{user_id}'),
                InlineKeyboardButton(text="𝟏𝟎", callback_data=f'beta {ID10}|{duration10}|{user_id}')
            ],
            [ 
                InlineKeyboardButton(text="رجوع", callback_data=f'chonga 2|{query}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="اغلاق", callback_data=f"ppcl2 smex|{user_id}")
            ],
        ]
    return buttons     
      
def gets(videoid, user_id):
    buttons= [
            [
                InlineKeyboardButton(text="تحميل صوت", callback_data=f'gets audio|{videoid}|{user_id}'),
                InlineKeyboardButton(text="تحميل فيديو", callback_data=f'gets video|{videoid}|{user_id}')
            ],
            [
                InlineKeyboardButton(text="اغلاق", callback_data=f'close2')
            ],
        ]
    return buttons


