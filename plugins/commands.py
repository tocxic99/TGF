import os
import sys
import asyncio 
from database import Db, db
from config import Config, temp
from script import Script
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument
import psutil
import time as time
from os import environ, execle, system

START_TIME = time.time()

# ============ MAIN MENU BUTTONS ============
main_buttons = [[
    InlineKeyboardButton('🌥 Uᴘᴅᴀᴛᴇ 🌥', url='https://t.me/+m7mFkK5rb9dhZDQ1'),
    InlineKeyboardButton('🍁 Sᴜᴘᴘᴏʀᴛ 🍁', url='https://t.me/RoRoNoi_bot')
],[
    InlineKeyboardButton('Hᴇʟᴘ 🌺', callback_data='help'),
    InlineKeyboardButton('Aʙᴏᴜᴛ 💌', callback_data='about')
],[
    InlineKeyboardButton('Sᴇᴛᴛɪɴɢs ⚙️', callback_data='settings#main')
],[
    InlineKeyboardButton('💎 ᴍʏ ᴘʟᴀɴ 💎', callback_data='my_plan_cb')
]]


@Client.on_message(filters.private & filters.command(['start']))
async def start(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await client.send_message(
        chat_id=message.chat.id,
        reply_markup=reply_markup,
        text=Script.START_TXT.format(user.first_name),
        disable_web_page_preview=True
    )


@Client.on_message(filters.private & filters.command(['restart']) & filters.user(Config.BOT_OWNER))
async def restart(client, message):
    msg = await message.reply_text(text="<i>Trying to restarting.....</i>")
    await asyncio.sleep(5)
    await msg.edit("<i>Server restarted successfully ✅</i>")
    system("git pull -f && pip3 install --no-cache-dir -r requirements.txt")
    execle(sys.executable, sys.executable, "main.py", environ)


# ============ HELP CALLBACK ============
@Client.on_callback_query(filters.regex(r'^help$'))
async def helpcb(bot, query):
    buttons = [[
        InlineKeyboardButton('🤔 ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴇ', callback_data='how_to_use')
    ],[
        InlineKeyboardButton('Aʙᴏᴜᴛ 💌', callback_data='about'),
        InlineKeyboardButton('Sᴇᴛᴛɪɴɢs ⚙️', callback_data='settings#main')
    ],[
        InlineKeyboardButton('• Back', callback_data='back')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.HELP_TXT,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


# ============ HOW TO USE CALLBACK ============
@Client.on_callback_query(filters.regex(r'^how_to_use$'))
async def how_to_use(bot, query):
    buttons = [[InlineKeyboardButton('• Back', callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.HOW_USE_TXT,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


# ============ BACK CALLBACK ============
@Client.on_callback_query(filters.regex(r'^back$'))
async def back(bot, query):
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await query.message.edit_text(
        reply_markup=reply_markup,
        text=Script.START_TXT.format(query.from_user.first_name),
        disable_web_page_preview=True
    )


# ============ ABOUT CALLBACK ============
@Client.on_callback_query(filters.regex(r'^about$'))
async def about(bot, query):
    buttons = [[
        InlineKeyboardButton('• Back', callback_data='help'),
        InlineKeyboardButton('Stats 📊', callback_data='status')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.ABOUT_TXT,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


# ============ STATUS CALLBACK ============
@Client.on_callback_query(filters.regex(r'^status$'))
async def status(bot, query):
    users_count, bots_count = await db.total_users_bots_count()
    forwardings = await db.forwad_count()
    premium_count = len(await db.get_all_premium_users())
    upt = await get_bot_uptime(START_TIME)
    buttons = [[
        InlineKeyboardButton('• Back', callback_data='help'),
        InlineKeyboardButton('System Stats 🧾', callback_data='systm_sts'),
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Script.STATUS_TXT.format(upt, users_count, premium_count, forwardings),
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )


# ============ SYSTEM STATUS CALLBACK ============
@Client.on_callback_query(filters.regex(r'^systm_sts$'))
async def sys_status(bot, query):
    buttons = [[InlineKeyboardButton('• back', callback_data='help')]]
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()
    disk_usage = psutil.disk_usage('/')
    total_space = disk_usage.total / (1024**3)
    used_space = disk_usage.used / (1024**3)
    free_space = disk_usage.free / (1024**3)
    text = f"""
╔════❰ sᴇʀᴠᴇʀ sᴛᴀᴛs  ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼ <b>ᴛᴏᴛᴀʟ ᴅɪsᴋ sᴘᴀᴄᴇ</b>: <code>{total_space:.2f} GB</code>
║┣⪼ <b>ᴜsᴇᴅ</b>: <code>{used_space:.2f} GB</code>
║┣⪼ <b>ꜰʀᴇᴇ</b>: <code>{free_space:.2f} GB</code>
║┣⪼ <b>ᴄᴘᴜ</b>: <code>{cpu}%</code>
║┣⪼ <b>ʀᴀᴍ</b>: <code>{ram}%</code>
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪
"""
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )


# ============ MY PLAN (Start menu se) ============
@Client.on_callback_query(filters.regex(r'^my_plan_cb$'))
async def my_plan_cb(bot, query):
    from datetime import datetime
    user_id = query.from_user.id

    if await db.is_premium(user_id):
        info = await db.get_premium_info(user_id)
        expiry = datetime.fromisoformat(info['expiry'])
        days_left = max(0, (expiry - datetime.now()).days)
        text = Script.PLAN_PREMIUM_TXT.format(
            expiry.strftime('%d %b %Y, %I:%M %p'),
            days_left,
            Config.PREMIUM_CONTACT
        )
    else:
        usage = await db.get_usage(user_id)
        used = usage.get('count', 0)
        limit = Config.FREE_LIMIT
        remaining = max(0, limit - used)
        text = Script.PLAN_FREE_TXT.format(
            limit, used, remaining,
            Config.PREMIUM_PRICE,
            Config.PREMIUM_CONTACT
        )

    buttons = [[InlineKeyboardButton('• Back', callback_data='back')]]
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )


# ============ BOT UPTIME ============
async def get_bot_uptime(start_time):
    uptime_seconds = int(time.time() - start_time)
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    uptime_weeks = uptime_days // 7
    uptime_string = ""
    if uptime_weeks != 0:
        uptime_string += f" {uptime_weeks}W"
    if uptime_days != 0:
        uptime_string += f" {uptime_days % 7}D"
    if uptime_hours != 0:
        uptime_string += f" {uptime_hours % 24}H"
    if uptime_minutes != 0:
        uptime_string += f" {uptime_minutes % 60}M"
    uptime_string += f" {uptime_seconds % 60} Sec"
    return uptime_string
