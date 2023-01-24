import os
import re
import yt_dlp
import aiohttp
import random
import asyncio
import shutil
import aiofiles
import requests
import time as sedtime

from os import path
from time import time
from .. import converter
from asyncio import QueueEmpty

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)
from pytgcalls import StreamType
from Yukki.config import LOG_GROUP_ID
from youtubesearchpython import VideosSearch
from ..YukkiUtilities.tgcallsrun import ASS_ACC
from Yukki import app, BOT_USERNAME, dbb, SUDOERS
from pytgcalls.types.input_stream import InputAudioStream, InputStream
from aiohttp import ClientResponseError, ServerTimeoutError, TooManyRedirects
from Yukki import dbb, app, BOT_USERNAME, BOT_ID, ASSID, ASSNAME, ASSUSERNAME, ASSMENTION
from Yukki.YukkiUtilities.tgcallsrun import (yukki, convert, download, clear, get, is_empty, put, task_done, smexy)
from ..YukkiUtilities.tgcallsrun import (yukki, convert, download, clear, get, is_empty, put, task_done)
from Yukki.YukkiUtilities.helpers.decorators import errors
from Yukki.YukkiUtilities.helpers.filters import command, other_filters
from Yukki.YukkiUtilities.helpers.paste import paste
from Yukki.YukkiUtilities.tgcallsrun import (yukki, clear, get, is_empty, put, task_done)
from Yukki.YukkiUtilities.database.queue import (is_active_chat, add_active_chat, remove_active_chat, music_on, is_music_playing, music_off)
from Yukki.YukkiUtilities.database.playlist import (get_playlist_count, _get_playlists, get_note_names, get_playlist, save_playlist, delete_playlist)
from Yukki.YukkiUtilities.database.assistant import (_get_assistant, get_assistant, save_assistant)
from Yukki.YukkiUtilities.helpers.inline import (play_keyboard, search_markup, play_markup, playlist_markup, audio_markup)
from Yukki.YukkiUtilities.helpers.inline import play_keyboard, confirm_keyboard, play_list_keyboard, close_keyboard, confirm_group_keyboard
from Yukki.YukkiUtilities.tgcallsrun import (yukki, convert, download, clear, get, is_empty, put, task_done, smexy)
from Yukki.YukkiUtilities.database.queue import (is_active_chat, add_active_chat, remove_active_chat, music_on, is_music_playing, music_off)
from Yukki.YukkiUtilities.database.onoff import (is_on_off, add_on, add_off)
from Yukki.YukkiUtilities.database.blacklistchat import (blacklisted_chats, blacklist_chat, whitelist_chat)
from Yukki.YukkiUtilities.database.gbanned import (get_gbans_count, is_gbanned_user, add_gban_user, add_gban_user)
from Yukki.YukkiUtilities.database.theme import (_get_theme, get_theme, save_theme)
from Yukki.YukkiUtilities.database.assistant import (_get_assistant, get_assistant, save_assistant)
from ..config import DURATION_LIMIT, ASS_ID
from ..YukkiUtilities.helpers.decorators import errors
from ..YukkiUtilities.helpers.filters import command
from ..YukkiUtilities.helpers.gets import (get_url, themes, random_assistant, ass_det)
from ..YukkiUtilities.helpers.thumbnails import gen_thumb
from ..YukkiUtilities.helpers.chattitle import CHAT_TITLE
from ..YukkiUtilities.helpers.ytdl import ytdl_opts 
from ..YukkiUtilities.helpers.inline import (play_keyboard, search_markup, play_markup, playlist_markup)

from pykeyboard import InlineKeyboard
from Yukki import aiohttpsession as session

pattern = re.compile(
    r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$"
)

flex = {}

async def isPreviewUp(preview: str) -> bool:
    for _ in range(7):
        try:
            async with session.head(preview, timeout=2) as resp:
                status = resp.status
                size = resp.content_length
        except asyncio.exceptions.TimeoutError:
            return False
        if status == 404 or (status == 200 and size == 0):
            await asyncio.sleep(0.4)
        else:
            return True if status == 200 else False
    return False

    
@Client.on_callback_query(filters.regex(pattern=r"ppcl"))
async def close_deleteTrue(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id 
    try:
        smex, user_id = callback_request.split("|") 
    except Exception as e:
        await CallbackQuery.message.edit(f"✶ حدث خطأ\n\n**السبب:** `{e}`")
        return 
    if CallbackQuery.from_user.id != int(user_id):
        await CallbackQuery.answer("✶ هذا الامر لايخصك", show_alert=True)
        return
    await CallbackQuery.message.delete()
    
    
@Client.on_callback_query(filters.regex("pausevc"))
async def off_pauseTrue(_, CallbackQuery):
    a = await app.get_chat_member(CallbackQuery.message.chat.id , CallbackQuery.from_user.id)
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer("✶ يجب ان تكن مشرفًا بصلاحية ادارة المحادثات الصوتية. ", show_alert=True)
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
        if await is_music_playing(chat_id):
            await yukki.pytgcalls.pause_stream(chat_id)
            await music_off(chat_id)
            await CallbackQuery.answer("✶ تم الايقاف مؤقتًا بنجاح")
            await CallbackQuery.edit_message_text(f"✶ تم الايقاف مسبقًا", reply_markup=play_keyboard)
        else:
            await CallbackQuery.answer(f"✶ قائمة التشغيل فارغة", show_alert=True)
            return
    else:
        await CallbackQuery.answer(f"✶ قائمة التشغيل فارغة", show_alert=True)
   
    
@Client.on_callback_query(filters.regex("resumevc"))
async def on_resumeTrue(_, CallbackQuery):  
    a = await app.get_chat_member(CallbackQuery.message.chat.id , CallbackQuery.from_user.id)
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer("✶ يجب ان تكن مشرفًا بصلاحية ادارة المكلمات الصوتية. ", show_alert=True)
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
        if await is_music_playing(chat_id):
            await CallbackQuery.answer("✶ قائمة التشغيل فارغة", show_alert=True)
            return    
        else:
            await music_on(chat_id)
            await yukki.pytgcalls.resume_stream(chat_id)
            await CallbackQuery.answer("✶ تم استئناف التشغيل")
            await CallbackQuery.edit_message_text(f"✶ تم استئناف التشغيل بنجاح", reply_markup=play_keyboard)
    else:
        await CallbackQuery.answer(f"✶ قائمة التشغيل فارغة", show_alert=True)
   
    
@Client.on_callback_query(filters.regex("skipvc"))
async def skip_changeTrue(_, CallbackQuery): 
    a = await app.get_chat_member(CallbackQuery.message.chat.id , CallbackQuery.from_user.id)
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer("✶ يجب ان تكن مشرفًا بصلاحية ادارة مكالمات صوتية ", show_alert=True)
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
        task_done(CallbackQuery.message.chat.id)
        if is_empty(CallbackQuery.message.chat.id):
            await remove_active_chat(chat_id)
            await CallbackQuery.answer("✶ قائمة التشغيل فارغة, تم مغادرة المكالمة بنجاح", show_alert=True)
            await yukki.pytgcalls.leave_group_call(chat_id)
            return
        else:
            await CallbackQuery.answer("تم تخطي التشغيل بنجاح", show_alert=True)
            afk = get(chat_id)['file']
            f1 = (afk[0])
            f2 = (afk[1])
            f3 = (afk[2])
            finxx = (f"{f1}{f2}{f3}")
            if str(finxx) != "raw":   
                mystic = await app.send_message(chat_id, "✶ جار تحميل الصوت من قائمة التشغيل")
                url = (f"https://www.youtube.com/watch?v={afk}")
                try:
                    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                        x = ytdl.extract_info(url, download=False)
                except Exception as e:
                    return await mystic.edit(f"failed to download this song.\n\n**reason:** `{e}`") 
                title = (x["title"])
                videoid = afk
                def my_hook(d):
                    if d['status'] == 'downloading':
                        percentage = d['_percent_str']
                        per = (str(percentage)).replace(".","", 1).replace("%","", 1)
                        per = int(per)
                        eta = d['eta']
                        speed = d['_speed_str']
                        size = d['_total_bytes_str']
                        bytesx = d['total_bytes']
                        if str(bytesx) in flex:
                            pass
                        else:
                            flex[str(bytesx)] = 1
                        if flex[str(bytesx)] == 1:
                            flex[str(bytesx)] += 1
                            sedtime.sleep(1)
                            mystic.edit(f"✶ جار تحميل {title[:50]}\n\n**✶ الحجم:** {size}\n**✶ تم تحميل:** {percentage}\n**✶ السرعة:** {speed}")
                        if per > 500:    
                            if flex[str(bytesx)] == 2:
                                flex[str(bytesx)] += 1
                                sedtime.sleep(0.5)
                                mystic.edit(f"✶ جار تحميل {title[:50]}...\n\n**✶ الحجم:** {size}\n**Downloaded:** {percentage}\n**✶ السرعة:** {speed}")
                                print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds")
                        if per > 800:    
                            if flex[str(bytesx)] == 3:
                                flex[str(bytesx)] += 1
                                sedtime.sleep(0.5)
                                mystic.edit(f"✶ جار تحميل {title[:50]}....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}")
                                print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds")
                        if per == 1000:    
                            if flex[str(bytesx)] == 4:
                                flex[str(bytesx)] = 1
                                sedtime.sleep(0.5)
                                mystic.edit(f"✶ جار تحميل {title[:50]}.....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}") 
                                print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} in {chat_title} | ETA: {eta} seconds")
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, download, url, my_hook)
                file = await convert(data)
                await yukki.pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputAudioStream(
                            file,
                        ),
                    ),
                )
                await mystic.delete()
                thumbnail = (x["thumbnail"])
                duration = (x["duration"])
                duration = round(x["duration"] / 60)
                theme = random.choice(themes)
                ctitle = (await app.get_chat(chat_id)).title
                ctitle = await CHAT_TITLE(ctitle)
                f2 = open(f'search/{afk}id.txt', 'r')        
                userid = (f2.read())
                thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)
                user_id = userid
                buttons = play_markup(videoid, user_id)
                semx = await app.get_users(userid)
                await app.send_photo(
                    chat_id,
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),    
                    caption=(f"✶ **تم التخطي الى التشغيل التالي**\n\n✶ **الأسم** {title[:80]}\n✶ **المدة:** `{duration}`\n✶ **بطلب من:** {semx.mention}"),
                )   
                os.remove(thumb)
            else:      
                await yukki.pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputAudioStream(
                            afk,
                        ),
                    ),
                )
                await mystic.delete()
                _chat_ = ((str(afk)).replace("_","", 1).replace("/","", 1).replace(".","", 1))
                f2 = open(f'search/{_chat_}title.txt', 'r')        
                title =(f2.read())
                f3 = open(f'search/{_chat_}duration.txt', 'r')        
                duration =(f3.read())
                f4 = open(f'search/{_chat_}username.txt', 'r')        
                username =(f4.read())
                f4 = open(f'search/{_chat_}videoid.txt', 'r')        
                videoid =(f4.read())
                user_id = 1
                videoid = str(videoid)
                if videoid == "smex1":
                    buttons = audio_markup(videoid, user_id)
                else:
                    buttons = play_markup(videoid, user_id)   
                await app.send_photo(
                    chat_id,
                    photo=f"downloads/{_chat_}final.png",
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"✶ **تم التخطي الى التشغيل التالي**\n\n✶ **الأسم:** {title[:80]}\n✶ **المدة:** `{duration}`\n✶ **بطلب من:** {username}",
                )
                return           
            
    
@Client.on_callback_query(filters.regex("cbcmds"))
async def cbcmds(_, query: CallbackQuery):
    await query.answer("قائمة الاوامر")
    await query.edit_message_text(
        f"""✶ اهلاً بك .\n\n ✶  قم بالضغط علي الزر الذي تريده لمعرفه الاوامر لكل فئه منهم !**""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("اوامر الاعضاء", callback_data="cbbasic"),
                    InlineKeyboardButton("اوامر المشرفين", callback_data="cbadmin"),
                ],
                [
                    InlineKeyboardButton(
                        "قناة البوت", url="https://t.me/Y88F8"
                    )
                ],
            ]
        ),
    )


@Client.on_callback_query(filters.regex("cbbasic"))
async def cbbasic(_, query: CallbackQuery):
    await query.answer("الاوامر الاساسيه")
    await query.edit_message_text(
        f"""
 
✶ /play - لتشغيل اغنية بالمكالمة


✶ /playlist - تظهر لك قائمة التشغيل

✶ /end , /stop - لانهاء التشغيل

✶ بحث - اسم الاغنيه اللي تبي تحمله

✶ /vsong - اسم الفيديو اللي تبيه يتحمل

✶ /skip - لتخطي التشغيل

✶ /search + اسم اللي تبي تبحث عنه

✶ /ping ـ إظهار حالة البوت بنق

✶ /uptime ـ لعرض مده التشغيل للبوت

✶ قناة البوت @Y88F8""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("✶ رجوع", callback_data="cbcmds")]]
        ),
    )

@Client.on_callback_query(filters.regex("nx"))
async def ava(_, query: CallbackQuery):
   if not query.from_user.id == query.message.reply_to_message.from_user.id:
          return await query.answer("- الأمر لايخصك", show_alert=True)
          
   rl = random.randint(3,446)
   url = f"https://t.me/foravaboys/{rl}"
   user = query.from_user.mention
   await query.edit_message_media(InputMediaPhoto(url, caption=f"༄ {user}\n༄ تم اختيار افتار لك"), reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "التالي", callback_data="nx")
                ],
            ]
        ),
    )     
    
    
@Client.on_callback_query(filters.regex("nx2"))
async def ava2(_, query: CallbackQuery):
   if not query.from_user.id == query.message.reply_to_message.from_user.id:
          return await query.answer("- الأمر لايخصك", show_alert=True)
          
   rl = random.randint(3,201)
   url = f"https://t.me/foravaanime/{rl}"
   user = query.from_user.mention
   await query.edit_message_media(InputMediaPhoto(url, caption=f"༄ {user}\n༄ تم اختيار افتار لك"), reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "التالي", callback_data="nx2")
                ],
            ]
        ),
    )         

@Client.on_callback_query(filters.regex("cbadmin"))
async def cbadmin(_, query: CallbackQuery):
    await query.answer("اوامر المشرفين")
    await query.edit_message_text(
        f"""- هنا أوامر المشرفين:
✶ /pause - ايقاف التشغيل موقتآ

✶ /resume - استئناف التشغيل

✶ /stop - لإيقاف التشغيل

✶ /vmute - لكتم البوت

✶ /vunmute - لرفع الكتم عن البوت

✶ /volume - ضبط مستوئ الصوت

✶ /reload - لتحديث البوت و قائمة المشرفين

✶ /userbotjoin - لاستدعاء الحساب المساعد

✶ /userbotleave - لطرد الحساب المساعد

✶ قناة البوت @Y88F8""",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("✶ رجوع", callback_data="cbcmds")]]
        ),
    )
    
                        
@Client.on_callback_query(filters.regex("stopvc"))
async def end_stopTrue(_, CallbackQuery):
    a = await app.get_chat_member(CallbackQuery.message.chat.id , CallbackQuery.from_user.id)
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer("✶ يجب ان تكن مشرفًا بصلاحية ادارة مكالمات صوتية", show_alert=True)
    chat_id = CallbackQuery.message.chat.id
    if await is_active_chat(chat_id):
        try:
            clear(chat_id)
        except QueueEmpty:
            pass
        try:
            await yukki.pytgcalls.leave_group_call(chat_id)
        except Exception as e:
            pass
        await remove_active_chat(CallbackQuery.message.chat.id)
        await CallbackQuery.edit_message_text("✶ تم انهاء التشغيل بنجاح", reply_markup=close_keyboard)
    else:
        await CallbackQuery.answer(f"✶ قائمة الشتغيل فارغة", show_alert=True)


@Client.on_callback_query(filters.regex("play_playlist"))
async def play_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id 
    try:
        user_id, smex = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"✶ حدث خطأ\n**reason**: `{e}`")
    name = CallbackQuery.from_user.first_name
    chat_title = CallbackQuery.message.chat.title
    if str(smex) == "personal":
        if CallbackQuery.from_user.id != int(user_id):
            return await CallbackQuery.answer("✶ هذه ليست قائمة تشغيلك الخاصة", show_alert=True)
        _playlist = await get_note_names(CallbackQuery.from_user.id)
        if not _playlist:
            return await CallbackQuery.answer(f"✶ ليس لديك قائمة تشغيل خاصة على قاعدة بياناتنا", show_alert=True)
        else:
            await CallbackQuery.message.delete()
            logger_text=f"""✶ تم بدأ التشغيل

✶ القروب : {chat_title}
✶ بواسطة : {name}

✶ قائمة تشغيل شخصية"""
            mystic = await CallbackQuery.message.reply(f"✶ جار بدأ قائمة تشغيل {name} \n✶ بواسطة : {CallbackQuery.from_user.first_name}")   
            checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
            msg = f"Queued Playlist:\n\n"
            j = 0
            for note in _playlist:
                _note = await get_playlist(CallbackQuery.from_user.id, note)
                title = _note["title"]
                videoid = _note["videoid"]
                url = (f"https://www.youtube.com/watch?v={videoid}")
                duration = _note["duration"]
                if await is_active_chat(chat_id):
                    position = await put(chat_id, file=videoid)
                    j += 1
                    msg += f"{j}- {title[:50]}\n"
                    msg += f"Queued Position: {position}\n\n"
                    f20 = open(f'search/{videoid}id.txt', 'w')
                    f20.write(f"{user_id}") 
                    f20.close()
                else:
                    try:
                        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                            x = ytdl.extract_info(url, download=False)
                    except Exception as e:
                        return await mystic.edit(f"failed to download this track.\n\n**reason:** `{e}`") 
                    title = (x["title"])
                    thumbnail = (x["thumbnail"])
                    def my_hook(d): 
                        if d['status'] == 'downloading':
                            percentage = d['_percent_str']
                            per = (str(percentage)).replace(".","", 1).replace("%","", 1)
                            per = int(per)
                            eta = d['eta']
                            speed = d['_speed_str']
                            size = d['_total_bytes_str']
                            bytesx = d['total_bytes']
                            if str(bytesx) in flex:
                                pass
                            else:
                                flex[str(bytesx)] = 1
                            if flex[str(bytesx)] == 1:
                                flex[str(bytesx)] += 1
                                try:
                                    if eta > 2:
                                        mystic.edit(f"✶ جار تحميل {title[:50]}.....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}")
                                except Exception as e:
                                    pass
                            if per > 250:    
                                if flex[str(bytesx)] == 2:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:     
                                        mystic.edit(f"✶ جار تحميل {title[:50]}.....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}")
                                    print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
                            if per > 500:    
                                if flex[str(bytesx)] == 3:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:     
                                        mystic.edit(f"✶ جار تحميل {title[:50]}.....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}")
                                    print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
                            if per > 800:    
                                if flex[str(bytesx)] == 4:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:    
                                        mystic.edit(f"✶ جار تحميل {title[:50]}.....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}")
                                    print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
                        if d['status'] == 'finished': 
                            try:
                                taken = d['_elapsed_str']
                            except Exception as e:
                                taken = "00:00"
                            size = d['_total_bytes_str']
                            mystic.edit(f"**✶ تم تحميل {title[:50]}...**\n\n**✶ الحجم :** `{size}`\n**✶ الوقت:** `{taken}`s")
                            print(f"[{videoid}] Downloaded | Elapsed: {taken} seconds")  
                    loop = asyncio.get_event_loop()
                    xx = await loop.run_in_executor(None, download, url, my_hook)
                    file = await convert(xx)
                    await music_on(chat_id)
                    await add_active_chat(chat_id)
                    await yukki.pytgcalls.join_group_call(
                        chat_id,
                        InputStream(
                            InputAudioStream(
                                file,
                            ),
                        ),
                        stream_type=StreamType().local_stream,
                    )
                    await mystic.delete()
                    theme = random.choice(themes)
                    ctitle = CallbackQuery.message.chat.title
                    ctitle = await CHAT_TITLE(ctitle)
                    thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)  
                    buttons = play_markup(videoid, user_id)
                    m = await app.send_photo(
                        chat_id,
                        photo=thumb,
                        reply_markup=InlineKeyboardMarkup(buttons),    
                        caption=(f"✶ **الأسم:** [{title[:80]}]({url})\n✶ **المدة:** `{duration}`\n✶ **بواسطة:** {checking}"),
                    )   
                    os.remove(thumb)
        m = await CallbackQuery.message.reply_text("✶ جار الاضافة الى قائمة الانتظار")
        link = await paste(msg)
        preview = link + "/preview.png"
        urlxp = link + "/index.txt"
        a1 = InlineKeyboardButton(text=f"قائمة الانتظار", url=urlxp)
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                ],
                [
                    InlineKeyboardButton(text="اغلاق", callback_data=f'close2')
                ]    
            ]
        )
        if await isPreviewUp(preview):
            try:
                await CallbackQuery.message.reply_photo(
                    photo=preview, caption=f"✶ هذه قائمة الانتظار الخاصة بك {name}.\n\n✶ اذا كنت تريد ان تحذفها فقط استعمل الامر : /delmyplaylist", quote=False, reply_markup=key
                )
                await m.delete()
            except Exception:
                pass
        else:
            await CallbackQuery.message.reply_text(
                    text=msg, reply_markup=key
                )
            await m.delete()
    if str(smex) == "group":
        _playlist = await get_note_names(CallbackQuery.message.chat.id)
        if not _playlist:
            return await CallbackQuery.answer(f"✶ هذا القروب ليس لديه اي قائمة تشغيل على قاعدة بياناتنا. ", show_alert=True)
        else:
            await CallbackQuery.message.delete()
            logger_text=f"""✶ جار بدأ التشغيل

- القروب : {chat_title}
- بواسطة : {name} """
            mystic = await CallbackQuery.message.reply(f"✶ جار بدأ تشغيل قائمة تشغيل القروب\n🎧 ✶ بواسطة:  {CallbackQuery.from_user.first_name}")   
            checking = f"[{CallbackQuery.from_user.first_name}](tg://user?id={userid})"
            msg = f"✶ قائمة الانتظار :\n\n"
            j = 0
            for note in _playlist:
                _note = await get_playlist(CallbackQuery.message.chat.id, note)
                title = _note["title"]
                videoid = _note["videoid"]
                url = (f"https://www.youtube.com/watch?v={videoid}")
                duration = _note["duration"]
                if await is_active_chat(chat_id):
                    position = await put(chat_id, file=videoid)
                    j += 1
                    msg += f"{j}- {title[:50]}\n"
                    msg += f"Queued Position: {position}\n\n"
                    f20 = open(f'search/{videoid}id.txt', 'w')
                    f20.write(f"{user_id}") 
                    f20.close()
                else:
                    try:
                        with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
                            x = ytdl.extract_info(url, download=False)
                    except Exception as e:
                        return await mystic.edit(f"failed to download this track.\n\n**reason:** `{e}`") 
                    title = (x["title"])
                    thumbnail = (x["thumbnail"])
                    def my_hook(d): 
                        if d['status'] == 'downloading':
                            percentage = d['_percent_str']
                            per = (str(percentage)).replace(".","", 1).replace("%","", 1)
                            per = int(per)
                            eta = d['eta']
                            speed = d['_speed_str']
                            size = d['_total_bytes_str']
                            bytesx = d['total_bytes']
                            if str(bytesx) in flex:
                                pass
                            else:
                                flex[str(bytesx)] = 1
                            if flex[str(bytesx)] == 1:
                                flex[str(bytesx)] += 1
                                try:
                                    if eta > 2:
                                        mystic.edit(f"✶ جار تحميل {title[:50]}.....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}")
                                except Exception as e:
                                    pass
                            if per > 250:    
                                if flex[str(bytesx)] == 2:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:     
                                        mystic.edit(f"✶ جار تحميل {title[:50]}.....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}")
                                    print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
                            if per > 500:    
                                if flex[str(bytesx)] == 3:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:     
                                        mystic.edit(f"✶ جار تحميل {title[:50]}.....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}")
                                    print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
                            if per > 800:    
                                if flex[str(bytesx)] == 4:
                                    flex[str(bytesx)] += 1
                                    if eta > 2:    
                                        mystic.edit(f"✶ جار تحميل {title[:50]}.....\n\n**✶ الحجم:** {size}\n**✶ تم التحميل:** {percentage}\n**✶ السرعة:** {speed}")
                                    print(f"[{videoid}] Downloaded {percentage} at a speed of {speed} | ETA: {eta} seconds")
                        if d['status'] == 'finished': 
                            try:
                                taken = d['_elapsed_str']
                            except Exception as e:
                                taken = "00:00"
                            size = d['_total_bytes_str']
                            mystic.edit(f"**✶ تم تحميل : {title[:50]}...**\n\n**✶ الحجم :** `{size}`\n**✶ الوقت المستغرق :** `{taken}` sec")
                            print(f"[{videoid}] Downloaded | Elapsed: {taken} seconds")  
                    loop = asyncio.get_event_loop()
                    xx = await loop.run_in_executor(None, download, url, my_hook)
                    file = await convert(xx)
                    await music_on(chat_id)
                    await add_active_chat(chat_id)
                    await yukki.pytgcalls.join_group_call(
                        chat_id,
                        InputStream(
                            InputAudioStream(
                                file,
                            ),
                        ),
                        stream_type=StreamType().local_stream,
                    )
                    await mystic.delete()
                    theme = random.choice(themes)
                    ctitle = CallbackQuery.message.chat.title
                    ctitle = await CHAT_TITLE(ctitle)
                    thumb = await gen_thumb(thumbnail, title, userid, theme, ctitle)
                    buttons = play_markup(videoid, user_id)
                    m = await app.send_photo(
                        chat_id,
                        photo=thumb,
                        reply_markup=InlineKeyboardMarkup(buttons),    
                        caption=(f"✶ **الأسم:** [{title[:80]}]({url})\n✶ **المدة:** `{duration}`\n✶ **طلب بواسطة** {checking}"),
                    )
                    os.remove(thumb)
        m = await CallbackQuery.message.reply_text("✶ تم الاضافة الى قائمة الانتظار...")
        link = await paste(msg)
        preview = link + "/preview.png"
        urlxp = link + "/index.txt"
        a1 = InlineKeyboardButton(text=f"قائمة الانتظار", url=urlxp)
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                ],
                [
                    InlineKeyboardButton(text="اغلاق", callback_data=f'close2')
                ]    
            ]
        )
        if await isPreviewUp(preview):
            try:
                await CallbackQuery.message.reply_photo(
                    photo=preview, caption=f"✶ هذه قائمة التشغيل في القروب \n\n✶ اذا اردت ان تحذفها استخدم الأمر:  /delchatplaylist", quote=False, reply_markup=key
                )
                await m.delete()
            except Exception:
                pass
        else:
            await CallbackQuery.message.reply_text(
                    text=msg, reply_markup=key
                )
            await m.delete()


@Client.on_callback_query(filters.regex("group_playlist"))
async def start_group_playlist(_,CallbackQuery):
    a = await app.get_chat_member(CallbackQuery.message.chat.id , CallbackQuery.from_user.id)
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer("✶ هذا الامر للمشرفين فقط", show_alert=True)
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id 
    try:
        url,smex = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"✶ حدث خطأ\n\n**reason:** `{e}`")
    name = CallbackQuery.from_user.first_name
    _count = await get_note_names(chat_id)
    count = 0
    if not _count:
        sex = await CallbackQuery.answer("✶ تم الاضافة الى قائمة تشغيل القروب", show_alert=True)
    else:
        for smex in _count:
            count += 1
    count = int(count)
    if count == 30:
        return await CallbackQuery.answer("✶ يمكنك اضافة 30 مقطع الى قائمة التشغيل فقط", show_alert=True)
    try:
        url = (f"https://www.youtube.com/watch?v={url}")
        results = VideosSearch(url, limit=1)
        for result in results.result()["result"]:
            title = (result["title"])
            duration = (result["duration"])
            videoid = (result["id"])
    except Exception as e:
            return await CallbackQuery.message.reply_text(f"✶ حدث خطأ يرجى اعادة توجيه الرسالة الى @MDDDP \n\n**reason:** `{e}`") 
    _check = await get_playlist(chat_id, videoid)
    title = title[:50]
    if _check:
         return await CallbackQuery.answer("✶ تم الاضافة الى قائمة تشغيل القروب", show_alert=True)   
    assis = {
        "videoid": videoid,
        "title": title,
        "duration": duration,
    }
    await save_playlist(chat_id, videoid, assis)
    return await CallbackQuery.answer("✶ تم الاضافة الى قائمة تشغيل القروب !", show_alert=True)
  

@Client.on_callback_query(filters.regex("playlist"))
async def start_personal_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id 
    try:
        url,smex = callback_request.split("|") 
    except Exception as e:
        return await CallbackQuery.message.edit(f"✶ حدث خطأ \n\n**reason:** `{e}`")
    name = CallbackQuery.from_user.first_name
    _count = await get_note_names(userid)
    count = 0
    if not _count:
        sex = await CallbackQuery.answer("✶ تم الاضافة الى قائمة تشغيل القروب ", show_alert=True)
    else:
        for smex in _count:
            count += 1 
    count = int(count)
    if count == 30:
        if userid in SUDOERS:
            pass
        else:
            return await CallbackQuery.answer("✶ يمكنك اضافة 30 اغنية الى قائمة التشغيل فقط !", show_alert=True)
    try:
        url = (f"https://www.youtube.com/watch?v={url}")
        results = VideosSearch(url, limit=1)
        for result in results.result()["result"]:
            title = (result["title"])
            duration = (result["duration"])
            videoid = (result["id"])
    except Exception as e:
            return await CallbackQuery.message.reply_text(f"an error occured.\n\nplease forward to @MDDDP\n**Possible Reason:**{e}") 
    _check = await get_playlist(userid, videoid)
    if _check:
         return await CallbackQuery.answer("✶ تم اضافة هذا المقطع الى قائمتك مسبقًا", show_alert=True) 
    title = title[:50]    
    assis = {
        "videoid": videoid,
        "title": title,
        "duration": duration,
    }
    await save_playlist(userid, videoid, assis)
    return await CallbackQuery.answer("✶ تمت الاضافة الى قائمة تشغيلك الخاصة", show_alert=True)   
    

@Client.on_callback_query(filters.regex("P_list"))
async def P_list(_, CallbackQuery):
    _playlist = await get_note_names(CallbackQuery.from_user.id)
    if not _playlist:
        return await CallbackQuery.answer("✶ لايوجد لديك قائمة تشغيل خاصة على قاعدة بياناتنا.", show_alert=True)
    else:
        j = 0
        msg = f"✶ قائمتك :\n\n"
        for note in _playlist:
            j += 1
            _note = await get_playlist(CallbackQuery.from_user.id, note)
            title = _note["title"]
            duration = _note["duration"]
            msg += f"{j}- {title[:60]}\n"
            msg += f"Duration: {duration} min(s)\n\n"
        await CallbackQuery.message.delete()     
        m = await CallbackQuery.message.reply_text("✶ جار المعالجة")
        link = await paste(msg)
        preview = link + "/preview.png"
        print(link)
        urlxp = link + "/index.txt"
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
        a2 = InlineKeyboardButton(text=f" بدء قائمة تشعيل {user_name[:18]}", callback_data=f'play_playlist {user_id}|personal')
        a3 = InlineKeyboardButton(text=f"قائمة التشغييل", url=urlxp)
        key = InlineKeyboardMarkup(
            [
                [
                    a2,
                ],
                [
                    a3,
                    InlineKeyboardButton(text="اغلاق", callback_data=f'close2')
                ]    
            ]
        )
        if await isPreviewUp(preview):
            try:
                await CallbackQuery.message.reply_photo(
                    photo=preview, quote=False, reply_markup=key
                )
                await m.delete()
            except Exception as e :
                print(e)
                pass
        else:
            print("5")
            await CallbackQuery.message.reply_photo(
                    photo=link, quote=False, reply_markup=key
                )
            await m.delete()
    
    
@Client.on_callback_query(filters.regex("G_list"))
async def G_list(_, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    _playlist = await get_note_names(CallbackQuery.message.chat.id)
    if not _playlist:
        return await CallbackQuery.answer(f"✶ هذا القروب لا يملك قائمة تشغيل على قاعدة بياناتنا .", show_alert=True)
    else:
        j = 0
        msg = f"✶ قائمة تشغيل القروب :\n\n"
        for note in _playlist:
            j += 1
            _note = await get_playlist(CallbackQuery.message.chat.id, note)
            title = _note["title"]
            duration = _note["duration"]
            msg += f"{j}- {title[:60]}\n"
            msg += f"    Duration- {duration} Min(s)\n\n"
        await CallbackQuery.message.delete()
        m = await CallbackQuery.message.reply_text("✶ جار المعالجة")
        link = await paste(msg)
        preview = link + "/preview.png"
        urlxp = link + "/index.txt"
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
        a1 = InlineKeyboardButton(text=f"بدء قائمة تشغيل القروب", callback_data=f'play_playlist {user_id}|group')
        a3 = InlineKeyboardButton(text=f"قائمة التشغيل", url=urlxp)
        key = InlineKeyboardMarkup(
            [
                [
                    a1,
                ],
                [
                    a3,
                    InlineKeyboardButton(text="اغلاق", callback_data=f'close2')
                ]    
            ]
        )
        if await isPreviewUp(preview):
            try:
                await CallbackQuery.message.reply_photo(
                    photo=preview, quote=False, reply_markup=key
                )
                await m.delete()
            except Exception:
                pass
        else:
            await CallbackQuery.message.reply_photo(
                    photo=link, quote=False, reply_markup=key
                )
            await m.delete()
                       
        
@Client.on_callback_query(filters.regex("cbgroupdel"))
async def cbgroupdel(_, CallbackQuery):  
    a = await app.get_chat_member(CallbackQuery.message.chat.id , CallbackQuery.from_user.id)
    if not a.can_manage_voice_chats:
        return await CallbackQuery.answer("✶ هذا الأمر يخص المشرفين فقط", show_alert=True)
    _playlist = await get_note_names(CallbackQuery.message.chat.id)                                    
    if not _playlist:
        return await CallbackQuery.answer("✶ هذا القروب لايمتلك قائمة تشغيل", show_alert=True)
    else:
        titlex = []
        for note in _playlist:
            await delete_playlist(CallbackQuery.message.chat.id, note)
    await CallbackQuery.answer("✶ تم حذف قائمة تشغيل القروب", show_alert=True)
    if CallbackQuery.message.reply_to_message:
        await CallbackQuery.message.reply_to_message.delete()
        return await CallbackQuery.message.delete()
    else:
        return await CallbackQuery.message.delete()
    
    
@Client.on_callback_query(filters.regex("cbdel"))
async def delplcb(_, CallbackQuery):
    _playlist = await get_note_names(CallbackQuery.from_user.id)                                    
    if not _playlist:
        return await CallbackQuery.answer("✶ ليس لديك قائمة تشغيل", show_alert=True)
    else:
        titlex = []
        for note in _playlist:
            await delete_playlist(CallbackQuery.from_user.id, note)
    await CallbackQuery.answer("✶ تم حذف قائمة تشغيلك بنجاح", show_alert=True)
    if CallbackQuery.message.reply_to_message:
        await CallbackQuery.message.reply_to_message.delete()
        return await CallbackQuery.message.delete()
    else:
        return await CallbackQuery.message.delete()
