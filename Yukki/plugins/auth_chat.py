import re
import asyncio

from pyrogram import filters, Client
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)

from telegraph import upload_file
from pyrogram.errors import FloodWait
from ..YukkiUtilities.helpers.gets import (get_url, themes, random_assistant, ass_det)
from ..YukkiUtilities.helpers.logger import LOG_CHAT
from ..YukkiUtilities.helpers.chattitle import CHAT_TITLE
from Yukki.YukkiUtilities.database.blacklistchat import (blacklisted_chats, blacklist_chat, whitelist_chat)

from Yukki import dbb, app, BOT_USERNAME, BOT_ID, ASSID, ASSNAME, ASSUSERNAME, OWNER, SUDOERS
from ..YukkiUtilities.helpers.filters import command
from Yukki.YukkiUtilities.database.chats import (get_served_chats, is_served_chat,
                                                 add_served_chat, get_served_chats,
                                                 remove_served_chat)  

from ..config import LOG_GROUP_ID                                                                                             


@app.on_message(filters.command("auth") & filters.user(SUDOERS))
async def auth_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**✶ اكتب تفعيل + ايدي الجروب. "
        )
    chat_id = int(message.text.strip().split()[1])
    if not await is_served_chat(chat_id):
        await add_served_chat(chat_id)
        await message.reply_text("✶ تم تفعيل القروب واضافته الى قاعدة البيانات")
    else:
        await message.reply_text("✶ المجموعة مفعلة مسبقًا")


@app.on_message(command(["del"]) & filters.user(SUDOERS))
async def unauth_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**usage:**\n\n/del [chat_id]"
        )
    chat_id = int(message.text.strip().split()[1])
    if not await is_served_chat(chat_id):
        await message.reply_text("❌ This Chat not in database.")
        return
    try:
        await remove_served_chat(chat_id)
        await message.reply_text("❌ Chat removed from database.")
        return
    except Exception as e:
      await message.reply_text(f"error: `{e}`")


@app.on_message(filters.command("جلب القروبات", [".", ""]) & filters.user(SUDOERS))
async def blacklisted_chats_func(_, message: Message):
    served_chats = []
    text = "- **قروبات البوت :**\n\n"
    try:
        chats = await get_served_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception as e:
        await message.reply_text(f"error: `{e}`")
        return
    count = 0
    for served_chat in served_chats:
        
        try:
            title = (await app.get_chat(served_chat)).title
        except Exception:
            title = "Private"
        count += 1
        text += f"**{count}. {title}** [`{served_chat}`]\n"
    if not text:
        await message.reply_text("❌ **no allowed chats**")  
    else:
        await message.reply_text(text) 
        
@app.on_message(filters.command("لينك", [".", ""]) & filters.user(OWNER))    
async def getlink(client: Client, message: Message):
    chat_id = int(message.text.strip().split()[1])
    link = await app.export_chat_invite_link(chat_id)

    await message.reply_text(link)
    
@app.on_message(filters.private & filters.incoming & filters.command("start"))
async def kstr(client: Client, message: Message):
       usr = await client.get_users(message.from_user.id)
       user_id = message.from_user.id
       user_ab = message.from_user.username
       user_name = message.from_user.first_name
       bot = [5323054766]
       if user_id in bot:
          return
       await app.send_message(LOG_GROUP_ID, f"- قام {message.from_user.mention} \n\n- بعمل ستارت للبوت\n- ايديه `{user_id}`\n- معرفه {user_ab} \n -@ZDDDU")
       
       
    
@app.on_message(filters.command("ارفعني", [".", ""]) & filters.user(OWNER)) 
async def promote_me(client: Client, message: Message):
        chat_id = int(message.text.strip().split()[1])
        user_id = message.from_user.id
        await app.promote_chat_member(chat_id, user_id, can_pin_messages=True, can_invite_users=True, can_change_info=True, can_promote_members=True, can_restrict_members=True, can_manage_voice_chats=True, can_delete_messages=True, can_manage_chat=True)
        await message.reply_text("- أهلًا عزيزي المطور تم رفعك مشرف في القروب ")
 
 
            
            
@app.on_message(filters.new_chat_members)
async def new_chat(c: Client, m: Message):
    ch = m.chat.username
    gti = m.chat.title
    buttons = [[InlineKeyboardButton(gti, url=f"t.me/{ch}")]]
    reply_markup = InlineKeyboardMarkup(buttons)
    chat_id = m.chat.id
    bot_id = (await c.get_me()).id
    for member in m.new_chat_members:
        if member.id == bot_id:
            return await app.send_message(LOG_GROUP_ID, f"- تم تفعيل البوت بمجموعة جديدة\n- ايدي المجموعة: `{chat_id}`\n\n-يوزر القروب:  @{ch}\n- @ZDDDU ",
    reply_markup=reply_markup,
    ) 
    
@app.on_message(filters.command("id", [".", ""]) & ~filters.edited) 
async def khalid(client: Client, message: Message):
    usr = await client.get_chat(message.from_user.id)
    name = usr.first_name
    usr_id = message.from_user.id
    bio = (await client.get_chat(usr_id)).bio
    async for photo in client.iter_profile_photos(message.from_user.id, limit=1):
                    await message.reply_photo(photo.file_id, caption=f"""• 𝑵𝒂𝒎𝒆 -› {message.from_user.mention}\n• 𝑼𝒔𝒆𝒓 -› @{message.from_user.username}\n• 𝑰𝒅 -› {message.from_user.id}\n\n{bio}""", 
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        name, url=f"https://t.me/{message.from_user.username}")
                ],
            ]
        ),
    )
    
      
@app.on_message(filters.text & (filters.channel | filters.private))            
async def hhhki(client: Client, message: Message):
       msg = message.text
       usr = await client.get_chat(message.from_user.id)
       name = usr.first_name
       usr_id = message.from_user.id
       mention = message.from_user.mention
       bot = [5323054766]
       if usr_id in bot:
          return
       await app.send_message(LOG_GROUP_ID, f"- قام {mention} \n\n- بارسال رسالة للبوت \n\n- {msg} \n\n -@ZDDDU")
       
       
@app.on_message(filters.command("ㅤㅤㅤㅤ", [".", ""]) & filters.user(OWNER))
async def myinfo(client: Client, message: Message):
    usr = await client.get_chat(message.from_user.id)
    name = usr.first_name
    usr_id = message.from_user.id
    bio = (await client.get_chat(usr_id)).bio
    async for photo in client.iter_profile_photos(message.from_user.id, limit=1):
                    await message.reply_photo(photo.file_id, caption=f"""{bio}""", 
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        name, url=f"https://t.me/{message.from_user.username}")
                ],[
                    InlineKeyboardButton(
                        text=f" 𝑼𝒔𝒆𝒓 -› @{message.from_user.username}", url=f"https://t.me/{message.from_user.username}")
                ],[
                    InlineKeyboardButton(
                        text=f" 𝑰𝒅 -› {message.from_user.id}", url=f"https://t.me/{message.from_user.username}")
                ],[
                    InlineKeyboardButton(
                        text=f" ✯", url=f"https://t.me/MDDDJ")
                ],
            ]
        ),
    )        
       
       
@app.on_message(filters.command("نادي المطور", [".", ""]) & filters.group)
async def kstr(client: Client, message: Message):
       chat = message.chat.id
       ch = message.chat.username
       gti = message.chat.title
       link = await app.export_chat_invite_link(chat)
       usr = await client.get_users(message.from_user.id)
       user_id = message.from_user.id
       user_ab = message.from_user.username
       user_name = message.from_user.first_name
       buttons = [[InlineKeyboardButton(gti, url=f"{link}")]]
       reply_markup = InlineKeyboardMarkup(buttons)
       
       await app.send_message(LOG_GROUP_ID, f"- قام {message.from_user.mention} \n\n- بمناداتك عزيزي المطور\n- ايديه `{user_id}`\n- معرفه @{user_ab}\n- ايدي القروب `{message.chat.id}` \n- @{ch} -@ZDDDU",
       reply_markup=reply_markup,
       )
       await message.reply_text(
        f"""- تم ارسال ندائك الى المطور سيتم الرد عليك باقرب وقت.""", disable_web_page_preview=True     
    )                                                                                                                                                                                                                               

         
#############
                                                                                  

        
        
        
        
        
             
    
       
       

  
        
        
       
        
                  
