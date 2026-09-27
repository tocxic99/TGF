import re, asyncio
from database import Db, db
from config import Config, temp
from .test import CLIENT, get_client, iter_messages
from script import Script
import base64
from pyrogram.file_id import FileId
from pyrogram import Client, filters, enums 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import struct

CLIENT = CLIENT()
COMPLETED_BTN = InlineKeyboardMarkup(
  [[
    InlineKeyboardButton('💟 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ 💟', url='https://t.me/STEVEBOTZSUPPORT')
  ],[
    InlineKeyboardButton('💠 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 💠', url='https://t.me/SteveBotz')
  ]]
)
CANCEL_BTN = InlineKeyboardMarkup([[InlineKeyboardButton('• ᴄᴀɴᴄᴇʟ', 'terminate_frwd')]])

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")
  

def unpack_new_file_id(new_file_id):
    """Return file_id"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        struct.pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    return file_id


@Client.on_message(filters.command("unequify") & filters.private)
async def unequify(client, message):
   user_id = message.from_user.id
   temp.CANCEL[user_id] = False
   if temp.lock.get(user_id) and str(temp.lock.get(user_id))=="True":
      return await message.reply("**please wait until previous task complete**")
   _bot = await db.get_userbot(user_id)
   if not _bot:
      return await message.reply("<b>Need userbot to do this process. Please add a userbot using /settings</b>")
   target = await client.ask(user_id, text="**Forward the last message from target chat or send last message link.**\n/cancel - `cancel this process`")
   if target.text and target.text.startswith("/"):
      return await message.reply("**process cancelled !**")
   elif target.text:
      regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
      match = regex.match(target.text.replace("?single", ""))
      if not match:
         return await message.reply('**Invalid link**')
      chat_id = match.group(4)
      last_msg_id = int(match.group(5))
      if chat_id.isnumeric():
         chat_id  = int(("-100" + chat_id))
   elif target.forward_from_chat.type in [enums.ChatType.CHANNEL, 'supergroup']:
        last_msg_id = target.forward_from_message_id
        chat_id = target.forward_from_chat.username or target.forward_from_chat.id
   else:
        return await message.reply_text("**invalid !**")
   confirm = await client.ask(user_id, text="**send /yes to start the process and /no to cancel this process**")
   if confirm.text.lower() == '/no':
      return await confirm.reply("**process cancelled !**")
   sts = await confirm.reply("`processing..`")
   il = False
   data = _bot['session']
   try:
      bot = await get_client(data, is_bot=il)
      await bot.start()
   except Exception as e:
      return await sts.edit(e)
   try:
       k = await bot.send_message(chat_id, text="testing")
       await k.delete()
   except:
       await sts.edit(f"**please make your [userbot](t.me/{_bot['username']}) admin in target chat with full permissions**")
       return await bot.stop()
   MESSAGES = []
   DUPLICATE = []
   total=deleted=0
   temp.lock[user_id] = True
   temp.CANCEL[user_id] = False
   
   try:
     await sts.edit(Script.DUPLICATE_TEXT.format(total, deleted, "ᴘʀᴏɢʀᴇssɪɴɢ"), reply_markup=CANCEL_BTN)
     
     total_count = 0
     async for msg in bot.get_chat_history(chat_id, limit=1):
         if msg.id:
             total_count = msg.id
     
     async for message in iter_messages(bot, chat_id=chat_id, limit=total_count, offset=0):
        if temp.CANCEL.get(user_id) == True:
           await sts.edit(Script.DUPLICATE_TEXT.format(total, deleted, "ᴄᴀɴᴄᴇʟʟᴇᴅ"), reply_markup=COMPLETED_BTN)
           return await bot.stop()
        
        # Check for documents and videos
        file_id = None
        if message.document:
            file_id = unpack_new_file_id(message.document.file_id)
        elif message.video:
            file_id = unpack_new_file_id(message.video.file_id)
        # elif message.audio:
        #     file_id = unpack_new_file_id(message.audio.file_id)
        # elif message.photo:
        #     file_id = unpack_new_file_id(message.photo.file_id)
        
        if file_id:
            if file_id in MESSAGES:
               DUPLICATE.append(message.id)
            else:
               MESSAGES.append(file_id)
            total += 1
            
            # Show progress every 100 messages
            if total % 100 == 0:
               await sts.edit(Script.DUPLICATE_TEXT.format(total, deleted, "ᴘʀᴏɢʀᴇssɪɴɢ"), reply_markup=CANCEL_BTN)
            
            # Delete duplicates in batches of 100
            if len(DUPLICATE) >= 100:
               try:
                   await bot.delete_messages(chat_id, DUPLICATE)
                   deleted += len(DUPLICATE)
                   await sts.edit(Script.DUPLICATE_TEXT.format(total, deleted, "ᴘʀᴏɢʀᴇssɪɴɢ"), reply_markup=CANCEL_BTN)
                   DUPLICATE = []
               except Exception as e:
                   print(f"Error deleting messages: {e}")
                   continue
     
     if DUPLICATE:
        try:
            await bot.delete_messages(chat_id, DUPLICATE)
            deleted += len(DUPLICATE)
        except Exception as e:
            print(f"Error deleting remaining messages: {e}")
            
   except Exception as e:
       temp.lock[user_id] = False 
       await sts.edit(f"**ERROR**\n`{e}`")
       return await bot.stop()
   
   temp.lock[user_id] = False
   await sts.edit(Script.DUPLICATE_TEXT.format(total, deleted, "ᴄᴏᴍᴘʟᴇᴛᴇᴅ"), reply_markup=COMPLETED_BTN)
   await bot.stop()
