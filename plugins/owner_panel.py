from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from config import Config
from database import db

# ==================== STATE ====================
OWNER_STATE = {}


# ==================== MAIN PANEL ====================

def main_panel_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⭐️ ADD PREMIUM", callback_data="own_addprem"),
            InlineKeyboardButton("🚫 REMOVE PREMIUM", callback_data="own_rmprem"),
        ],
        [
            InlineKeyboardButton("💎 PREMIUM LIST", callback_data="own_premlist"),
            InlineKeyboardButton("👥 ALL USERS", callback_data="own_users"),
        ],
        [
            InlineKeyboardButton("🔍 USER INFO", callback_data="own_userinfo"),
            InlineKeyboardButton("🔄 RESET USAGE", callback_data="own_reset"),
        ],
        [
            InlineKeyboardButton("📢 BROADCAST ALL", callback_data="own_bc_all"),
            InlineKeyboardButton("💎 BROADCAST PREMIUM", callback_data="own_bc_prem"),
        ],
        [
            InlineKeyboardButton("🔨 BAN USER", callback_data="own_ban"),
            InlineKeyboardButton("✅ UNBAN USER", callback_data="own_unban"),
        ],
        [
            InlineKeyboardButton("📋 BANNED LIST", callback_data="own_banlist"),
        ],
        [
            InlineKeyboardButton("📊 STATISTICS", callback_data="own_stats"),
            InlineKeyboardButton("⚙️ SETTINGS", callback_data="own_settings"),
        ],
        [
            InlineKeyboardButton("🗑 DELETE USER", callback_data="own_deluser"),
            InlineKeyboardButton("💥 RESET ALL USAGE", callback_data="own_resetall"),
        ],
        [
            InlineKeyboardButton("❌ CLOSE PANEL", callback_data="own_close"),
        ]
    ])


async def build_main_text():
    total = await db.total_users_count()
    premium_users = await db.get_all_premium_users()
    banned = await db.get_banned()
    return (
        f"👑 <b>OWNER CONTROL PANEL</b> 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Total Users:</b> <code>{total}</code>\n"
        f"⭐️ <b>Premium Users:</b> <code>{len(premium_users)}</code>\n"
        f"🆓 <b>Free Users:</b> <code>{total - len(premium_users)}</code>\n"
        f"🚫 <b>Banned Users:</b> <code>{len(banned)}</code>\n"
        f"📊 <b>Free Lifetime Limit:</b> <code>{Config.FREE_LIMIT}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>🎯 Neeche buttons se sab kuch control karo 👇</i>"
    )


@Client.on_message(filters.command("owner") & filters.user(Config.BOT_OWNER) & filters.private)
async def owner_panel(client, message: Message):
    text = await build_main_text()
    await message.reply_text(text, reply_markup=main_panel_keyboard())


# ==================== CALLBACKS ====================

@Client.on_callback_query(filters.user(Config.BOT_OWNER) & filters.regex(r'^own_'))
async def owner_callbacks(client, query: CallbackQuery):
    data = query.data
    owner_id = query.from_user.id

    # ---------- CLOSE ----------
    if data == "own_close":
        try:
            await query.message.delete()
        except Exception:
            pass
        return

    # ---------- BACK ----------
    if data == "own_back":
        text = await build_main_text()
        await query.message.edit_text(text, reply_markup=main_panel_keyboard())
        return

    # ---------- ADD PREMIUM ----------
    if data == "own_addprem":
        OWNER_STATE[owner_id] = {'action': 'add_premium', 'step': 'waiting_uid'}
        await query.message.edit_text(
            "⭐️ <b>ADD PREMIUM</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 User ki <b>numeric ID</b> bhejo:\n\n"
            "<i>❌ Cancel: /cancel</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- REMOVE PREMIUM ----------
    if data == "own_rmprem":
        OWNER_STATE[owner_id] = {'action': 'remove_premium', 'step': 'waiting_uid'}
        await query.message.edit_text(
            "🚫 <b>REMOVE PREMIUM</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 User ki <b>ID</b> bhejo:\n\n"
            "<i>❌ Cancel: /cancel</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- PREMIUM LIST ----------
    if data == "own_premlist":
        users = await db.get_all_premium_users()
        if not users:
            await query.answer("😕 Koi premium user nahi hai!", show_alert=True)
            return
        text = f"💎 <b>PREMIUM USERS ({len(users)})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, u in enumerate(users[:50], 1):
            exp = u['premium']['expiry']
            if isinstance(exp, str):
                exp = datetime.fromisoformat(exp)
            days_left = max(0, (exp - datetime.now()).days)
            text += (
                f"<b>{i}.</b> ⭐️ <code>{u['id']}</code> — <b>{u.get('name','?')}</b>\n"
                f"    📅 <i>{exp.strftime('%d %b %Y')}</i> — <b>{days_left}d left</b>\n"
            )
        if len(users) > 50:
            text += f"\n<i>...aur {len(users)-50} users</i>"
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- ALL USERS ----------
    if data == "own_users":
        total = await db.total_users_count()
        text = f"👥 <b>ALL USERS ({total})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        cursor = db.col.find({}).sort('id', 1).limit(50)
        async for u in cursor:
            prem = "⭐️" if await db.is_premium(u['id']) else "🆓"
            ban = "🚫" if (u.get('ban_status') or {}).get('is_banned') else ""
            text += f"{prem} <code>{u['id']}</code> — {u.get('name','?')} {ban}\n"
        if total > 50:
            text += f"\n<i>...aur {total-50} users</i>"
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- USER INFO ----------
    if data == "own_userinfo":
        OWNER_STATE[owner_id] = {'action': 'user_info', 'step': 'waiting_uid'}
        await query.message.edit_text(
            "🔍 <b>USER INFO</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 User ki <b>ID</b> bhejo:\n\n"
            "<i>❌ Cancel: /cancel</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- RESET USAGE ----------
    if data == "own_reset":
        OWNER_STATE[owner_id] = {'action': 'reset_usage', 'step': 'waiting_uid'}
        await query.message.edit_text(
            "🔄 <b>RESET USAGE</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 User ki <b>ID</b> bhejo\n"
            "ya <code>all</code> bhejo sabka reset karne ke liye:\n\n"
            "<i>❌ Cancel: /cancel</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- BROADCAST ALL ----------
    if data == "own_bc_all":
        OWNER_STATE[owner_id] = {'action': 'bc_all', 'step': 'waiting_msg'}
        await query.message.edit_text(
            "📢 <b>BROADCAST — ALL USERS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📩 Jo message bhejna hai woh bhejo\n"
            "<i>(text/photo/video — kuch bhi)</i>\n\n"
            "<i>❌ Cancel: /cancel</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- BROADCAST PREMIUM ----------
    if data == "own_bc_prem":
        OWNER_STATE[owner_id] = {'action': 'bc_prem', 'step': 'waiting_msg'}
        await query.message.edit_text(
            "💎 <b>BROADCAST — PREMIUM USERS</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📩 Jo message bhejna hai woh bhejo:\n\n"
            "<i>❌ Cancel: /cancel</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- BAN USER ----------
    if data == "own_ban":
        OWNER_STATE[owner_id] = {'action': 'ban_user', 'step': 'waiting_uid'}
        await query.message.edit_text(
            "🔨 <b>BAN USER</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 User ki <b>ID</b> bhejo:\n\n"
            "<i>❌ Cancel: /cancel</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- UNBAN USER ----------
    if data == "own_unban":
        OWNER_STATE[owner_id] = {'action': 'unban_user', 'step': 'waiting_uid'}
        await query.message.edit_text(
            "✅ <b>UNBAN USER</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "👤 User ki <b>ID</b> bhejo:\n\n"
            "<i>❌ Cancel: /cancel</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- BANNED LIST ----------
    if data == "own_banlist":
        banned = await db.get_banned()
        if not banned:
            await query.answer("😇 Koi banned user nahi hai!", show_alert=True)
            return
        text = f"🚫 <b>BANNED USERS ({len(banned)})</b>\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, uid in enumerate(banned[:50], 1):
            text += f"<b>{i}.</b> 🚫 <code>{uid}</code>\n"
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- STATS ----------
    if data == "own_stats":
        total = await db.total_users_count()
        premium = await db.get_all_premium_users()
        banned = await db.get_banned()
        conv = (len(premium) / total * 100) if total else 0
        text = (
            f"📊 <b>BOT STATISTICS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👥 Total Users: <code>{total}</code>\n"
            f"⭐️ Premium Users: <code>{len(premium)}</code>\n"
            f"🆓 Free Users: <code>{total - len(premium)}</code>\n"
            f"🚫 Banned Users: <code>{len(banned)}</code>\n"
            f"📈 Conversion: <code>{conv:.1f}%</code>\n"
            f"📊 Free Lifetime Limit: <code>{Config.FREE_LIMIT}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 Bot Owner: <code>{Config.BOT_OWNER}</code>"
        )
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- SETTINGS ----------
    if data == "own_settings":
        text = (
            f"⚙️ <b>BOT SETTINGS</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Free Lifetime Limit: <code>{Config.FREE_LIMIT}</code>\n"
            f"💵 Premium Price: <code>{Config.PREMIUM_PRICE}</code>\n"
            f"💬 Contact: {Config.PREMIUM_CONTACT}\n"
            f"👑 Owner ID: <code>{Config.BOT_OWNER}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<i>💡 Settings change karne ke liye Koyeb pe env vars update karo.</i>"
        )
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- DELETE USER ----------
    if data == "own_deluser":
        OWNER_STATE[owner_id] = {'action': 'del_user', 'step': 'waiting_uid'}
        await query.message.edit_text(
            "🗑 <b>DELETE USER</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "⚠️ <b>WARNING:</b> Ye action user ko DB se hata dega!\n\n"
            "👤 User ki <b>ID</b> bhejo:\n\n"
            "<i>❌ Cancel: /cancel</i>",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 BACK", callback_data="own_back")
            ]])
        )
        return

    # ---------- RESET ALL USAGE (Lifetime) ----------
    if data == "own_resetall":
        await db.col.update_many(
            {},
            {'$set': {'usage': {'count': 0}}}
        )
        await query.answer("✅ Sab users ka lifetime usage reset ho gaya!", show_alert=True)
        return

    await query.answer("Unknown action", show_alert=True)


# ==================== TEXT INPUT HANDLER ====================

@Client.on_message(
    filters.user(Config.BOT_OWNER) & filters.private &
    ~filters.command([
        "start", "owner", "addpremium", "removepremium", "premiumusers",
        "resetuser", "broadcast", "stats", "cancel", "help", "myplan",
        "forward", "settings", "unequify", "stop", "reset", "restart",
        "resetall"
    ])
)
async def owner_text_handler(client, message: Message):
    owner_id = message.from_user.id
    state = OWNER_STATE.get(owner_id)
    if not state:
        return

    action = state['action']
    step = state['step']
    text = (message.text or "").strip()

    if text.lower() == "/cancel":
        OWNER_STATE.pop(owner_id, None)
        await message.reply_text("✅ Cancelled.")
        return

    # ========== USER INFO ==========
    if action == 'user_info' and step == 'waiting_uid':
        try:
            uid = int(text)
        except ValueError:
            return await message.reply_text("❌ Invalid ID.")
        user = await db.col.find_one({'id': uid})
        if not user:
            OWNER_STATE.pop(owner_id, None)
            return await message.reply_text("❌ User nahi mila.")
        is_prem = await db.is_premium(uid)
        usage = await db.get_usage(uid)
        prem_info = await db.get_premium_info(uid)
        prem_text = "🆓 Free User"
        if is_prem:
            exp = datetime.fromisoformat(prem_info['expiry'])
            days_left = max(0, (exp - datetime.now()).days)
            prem_text = f"⭐️ Premium — {days_left}d left ({exp.strftime('%d %b %Y')})"
        ban = user.get('ban_status') or {}
        ban_text = "🚫 Banned" if ban.get('is_banned') else "✅ Active"
        info = (
            f"🔍 <b>USER INFO</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Name: <b>{user.get('name','?')}</b>\n"
            f"🆔 ID: <code>{uid}</code>\n"
            f"📌 Status: {ban_text}\n"
            f"⭐️ Plan: {prem_text}\n"
            f"📊 Lifetime Used: <code>{usage.get('count',0)}/{Config.FREE_LIMIT}</code>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        OWNER_STATE.pop(owner_id, None)
        await message.reply_text(info)
        return

    # ========== ADD PREMIUM ==========
    if action == 'add_premium' and step == 'waiting_uid':
        try:
            uid = int(text)
        except ValueError:
            return await message.reply_text("❌ Invalid ID.")
        if not await db.is_user_exist(uid):
            return await message.reply_text("❌ User registered nahi hai. Pehle /start karwao.")
        state['uid'] = uid
        state['step'] = 'waiting_days'
        await message.reply_text(
            f"✅ User: <code>{uid}</code>\n\n"
            f"⏱ Ab <b>days</b> bhejo (default 30):\n"
            f"<i>Example: 30, 90, 365</i>\n\n"
            f"<i>❌ Cancel: /cancel</i>"
        )
        return

    if action == 'add_premium' and step == 'waiting_days':
        try:
            days = int(text) if text else 30
            if days <= 0:
                raise ValueError
        except ValueError:
            return await message.reply_text("❌ Valid number bhejo (1-3650).")
        uid = state['uid']
        expiry = await db.add_premium(uid, days)
        OWNER_STATE.pop(owner_id, None)
        await message.reply_text(
            f"✅ <b>Premium Activated!</b>\n\n"
            f"👤 User: <code>{uid}</code>\n"
            f"⏱ Days: <code>{days}</code>\n"
            f"📅 Expires: <code>{expiry.strftime('%d %b %Y, %I:%M %p')}</code>"
        )
        try:
            await client.send_message(
                uid,
                f"🎉 <b>Premium Activated!</b>\n\n"
                f"⏱ Duration: <code>{days} days</code>\n"
                f"📅 Expires: <code>{expiry.strftime('%d %b %Y, %I:%M %p')}</code>\n"
                f"♾ Now you have <b>UNLIMITED</b> forwarding!"
            )
        except Exception:
            pass
        return

    # ========== REMOVE PREMIUM ==========
    if action == 'remove_premium' and step == 'waiting_uid':
        try:
            uid = int(text)
        except ValueError:
            return await message.reply_text("❌ Invalid ID.")
        await db.remove_premium(uid)
        OWNER_STATE.pop(owner_id, None)
        await message.reply_text(f"✅ Premium removed from <code>{uid}</code>")
        try:
            await client.send_message(uid, "ℹ️ Aapka <b>Premium</b> hata diya gaya hai.")
        except Exception:
            pass
        return

    # ========== RESET USAGE (Lifetime) ==========
    if action == 'reset_usage' and step == 'waiting_uid':
        OWNER_STATE.pop(owner_id, None)
        if text.lower() == 'all':
            await db.col.update_many(
                {},
                {'$set': {'usage': {'count': 0}}}
            )
            return await message.reply_text("✅ Sab users ka lifetime usage reset ho gaya.")
        try:
            uid = int(text)
        except ValueError:
            return await message.reply_text("❌ Invalid ID.")
        await db.reset_user_usage(uid)
        await message.reply_text(f"✅ Lifetime usage reset for <code>{uid}</code>")
        return

    # ========== BAN USER ==========
    if action == 'ban_user' and step == 'waiting_uid':
        OWNER_STATE.pop(owner_id, None)
        try:
            uid = int(text)
        except ValueError:
            return await message.reply_text("❌ Invalid ID.")
        await db.ban_user(uid, "Banned by owner")
        await message.reply_text(f"🚫 User <code>{uid}</code> banned.")
        try:
            await client.send_message(uid, "🚫 Aapko bot se ban kar diya gaya hai.")
        except Exception:
            pass
        return

    # ========== UNBAN USER ==========
    if action == 'unban_user' and step == 'waiting_uid':
        OWNER_STATE.pop(owner_id, None)
        try:
            uid = int(text)
        except ValueError:
            return await message.reply_text("❌ Invalid ID.")
        await db.remove_ban(uid)
        await message.reply_text(f"✅ User <code>{uid}</code> unbanned.")
        try:
            await client.send_message(uid, "✅ Aapka ban hata diya gaya hai.")
        except Exception:
            pass
        return

    # ========== DELETE USER ==========
    if action == 'del_user' and step == 'waiting_uid':
        OWNER_STATE.pop(owner_id, None)
        try:
            uid = int(text)
        except ValueError:
            return await message.reply_text("❌ Invalid ID.")
        await db.delete_user(uid)
        await message.reply_text(f"🗑 User <code>{uid}</code> deleted from DB.")
        return

    # ========== BROADCAST ==========
    if action in ('bc_all', 'bc_prem') and step == 'waiting_msg':
        OWNER_STATE.pop(owner_id, None)

        if action == 'bc_all':
            users_cursor = db.col.find({})
        else:
            users_cursor = db.col.find({'premium.expiry': {'$ne': None}})

        success, failed = 0, 0
        status = await message.reply_text("📢 Broadcasting... 0 sent")

        count = 0
        async for u in users_cursor:
            uid = u['id']
            try:
                if action == 'bc_prem' and not await db.is_premium(uid):
                    continue
                await message.copy(uid)
                success += 1
            except Exception:
                failed += 1
            count += 1
            if count % 20 == 0:
                try:
                    await status.edit_text(
                        f"📢 <b>Broadcasting...</b>\n"
                        f"✅ Sent: <code>{success}</code>\n"
                        f"❌ Failed: <code>{failed}</code>"
                    )
                except Exception:
                    pass

        await status.edit_text(
            f"✅ <b>Broadcast Done!</b>\n\n"
            f"📢 Sent: <code>{success}</code>\n"
            f"❌ Failed: <code>{failed}</code>"
        )
        return


@Client.on_message(filters.command("cancel") & filters.user(Config.BOT_OWNER) & filters.private)
async def cancel_state(client, message: Message):
    if message.from_user.id in OWNER_STATE:
        OWNER_STATE.pop(message.from_user.id, None)
        await message.reply_text("✅ Cancelled.")
