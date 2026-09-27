from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from database import db


@Client.on_message(filters.command("myplan") & filters.private)
async def my_plan(client, message: Message):
    user_id = message.from_user.id
    if await db.is_premium(user_id):
        info = await db.get_premium_info(user_id)
        expiry = datetime.fromisoformat(info['expiry'])
        days_left = max(0, (expiry - datetime.now()).days)
        await message.reply_text(
            f"⭐️ <b>You are a PREMIUM user!</b>\n\n"
            f"📅 Expires: <code>{expiry.strftime('%d %b %Y, %I:%M %p')}</code>\n"
            f"⏳ Days left: <code>{days_left}</code>\n"
            f"♾ Daily limit: <b>UNLIMITED</b>\n\n"
            f"Thanks for supporting us ❤️"
        )
    else:
        usage = await db.get_usage(user_id)
        used = usage.get('count', 0)
        limit = Config.FREE_LIMIT
        remaining = max(0, limit - used)
        await message.reply_text(
            f"👤 <b>Plan:</b> 🆓 Free\n\n"
            f"📊 Daily limit: <code>{limit}</code>\n"
            f"✅ Used today: <code>{used}</code>\n"
            f"🔋 Remaining: <code>{remaining}</code>\n\n"
            f"⭐️ <b>Upgrade to Premium</b> for <b>UNLIMITED</b> forwarding!\n"
            f"💵 Price: <code>{Config.PREMIUM_PRICE}</code>\n"
            f"💬 Contact: {Config.PREMIUM_CONTACT}\n\n"
            f"<i>Limit resets daily at 12:00 AM.</i>"
        )


@Client.on_message(filters.command("addpremium") & filters.user(Config.BOT_OWNER) & filters.private)
async def add_premium(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: <code>/addpremium user_id [days]</code>")
    try:
        args = message.text.split()
        uid = int(args[1])
        days = int(args[2]) if len(args) > 2 else 30
        expiry = await db.add_premium(uid, days)
        await message.reply_text(
            f"✅ <b>Premium Activated!</b>\n\n"
            f"👤 User: <code>{uid}</code>\n"
            f"⏱ Days: <code>{days}</code>\n"
            f"📅 Expires: <code>{expiry.strftime('%d %b %Y, %I:%M %p')}</code>"
        )
        try:
            await client.send_message(uid, f"🎉 <b>Premium Activated!</b>\n⏱ {days} days\n♾ Unlimited forwarding!")
        except Exception:
            pass
    except Exception as e:
        await message.reply_text(f"❌ Error: <code>{e}</code>")


@Client.on_message(filters.command("removepremium") & filters.user(Config.BOT_OWNER) & filters.private)
async def remove_premium(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: <code>/removepremium user_id</code>")
    try:
        uid = int(message.command[1])
        await db.remove_premium(uid)
        await message.reply_text(f"✅ Premium removed from <code>{uid}</code>")
    except Exception as e:
        await message.reply_text(f"❌ Error: <code>{e}</code>")


@Client.on_message(filters.command("premiumusers") & filters.user(Config.BOT_OWNER) & filters.private)
async def list_premium(client, message: Message):
    users = await db.get_all_premium_users()
    if not users:
        return await message.reply_text("No active premium users.")
    text = f"⭐️ <b>Premium Users:</b> <code>{len(users)}</code>\n\n"
    for u in users[:50]:
        exp = u['premium']['expiry']
        if isinstance(exp, str):
            exp = datetime.fromisoformat(exp)
        text += f"⭐️ <code>{u['id']}</code> — {u.get('name','?')} — {exp.strftime('%d %b %Y')}\n"
    await message.reply_text(text)