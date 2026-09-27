from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import UserNotParticipant
from config import Config
from script import Script


def get_force_sub_buttons():
    buttons = []
    for ch_id, link in Config.FORCE_SUB_CHANNELS:
        buttons.append([InlineKeyboardButton(f"📢 Join {ch_id}", url=link)])
    buttons.append([InlineKeyboardButton("✅ I Have Joined", callback_data="check_joined")])
    return InlineKeyboardMarkup(buttons)


async def is_user_joined(client, user_id):
    for ch_id, _ in Config.FORCE_SUB_CHANNELS:
        try:
            member = await client.get_chat_member(ch_id, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except UserNotParticipant:
            return False
        except Exception:
            continue
    return True


@Client.on_message(filters.private, group=-1)
async def force_sub_check(client, message: Message):
    if not Config.FORCE_SUB_CHANNELS:
        return
    user_id = message.from_user.id
    if user_id == Config.BOT_OWNER:
        return
    if await is_user_joined(client, user_id):
        return
    await message.reply_text(
        Script.FORCE_SUB_TXT,
        reply_markup=get_force_sub_buttons()
    )
    message.stop_propagation()


@Client.on_callback_query(filters.regex(r'^check_joined$'))
async def check_joined(client, query: CallbackQuery):
    user_id = query.from_user.id
    if await is_user_joined(client, user_id):
        await query.answer("✅ Thanks for joining!", show_alert=True)
        try:
            await query.message.delete()
        except Exception:
            pass
    else:
        await query.answer("❌ Aapne saare channels join nahi kiye!", show_alert=True)
