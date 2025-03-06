from aiogram.types import Message
from aiogram import F
from loader import dp,db,bot,CHANNELS
from aiogram.filters import CommandStart,Command,and_f
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time
from aiogram.types import Message,ChatPermissions
import logging
import asyncio

logging.basicConfig(level=logging.INFO)

# /start komandasi
@dp.message(CommandStart())
async def start_command(message: Message):
    full_name = message.from_user.full_name
    user_name = message.from_user.full_name
    telegram_id = message.from_user.id
    try:
        db.add_user(full_name=full_name, telegram_id=telegram_id)  # Foydalanuvchi bazaga qo'shildi
        await message.answer(text=f"👋 Salom {user_name}!\n\n"
        "Men sizning botingizman va quyidagi funktsiyalarni bajarishim mumkin:\n\n"
        "🔧 Iltimos, buyruqlarni tekshirish uchun /help komandasini yuboring.\n"
        "ℹ️ Ma'lumot uchun /about komandasini yuboring.\n\n"
        "Sizga yordam bera olishim uchun tayyorman! 😊\n\n"
        "Guruhdagi buyruqlarni ishlatishda ehtiyot bo'ling va ehtiyojlaringiz bo'lsa, adminlarga murojaat qiling.")
    except:
        await message.answer(text=f"👋 Salom {user_name}!\n\n"
        "Men sizning botingizman va quyidagi funktsiyalarni bajarishim mumkin:\n\n"
        "🔧 Iltimos, buyruqlarni tekshirish uchun /help komandasini yuboring.\n"
        "ℹ️ Ma'lumot uchun /about komandasini yuboring.\n\n"
        "Sizga yordam bera olishim uchun tayyorman! 😊\n\n"
        "Guruhdagi buyruqlarni ishlatishda ehtiyot bo'ling va ehtiyojlaringiz bo'lsa, adminlarga murojaat qiling.")


# Guruhga yangi a'zo qo'shilganda
@dp.message(F.new_chat_members)
async def new_member(message: Message):
    for user in message.new_chat_members:  # Bir nechta odam qo‘shilgan bo‘lishi mumkin
        user_name = user.full_name
        welcome_message = f"🎉 {user_name}, guruhimizga xush kelibsiz! 😊\nSiz bilan tanishishdan mamnunmiz! 🌟"
    
    await message.delete()  # "вступил(а) в группу" xabarini o‘chirish
    sent_message = await message.answer(welcome_message)  # Bot yuborgan xabar
    await asyncio.sleep(60)  # 60 soniya kutish
    await sent_message.delete()  # Botning xabarini o‘chirish

# Guruhdan a'zo chiqib ketganda
@dp.message(F.left_chat_member)
async def member_left(message: Message):
    user = message.left_chat_member  # Bu dict emas, balki User obyekti
    user_name = user.full_name
    goodbye_message = f"😢 {user_name}, siz bilan xayrlashamiz! 🌙\nYana qaytib kelishingizni kutamiz! 🙌"
    
    await message.delete()  # "покинул(а) группу" xabarini o‘chirish
    sent_message = await message.answer(goodbye_message)  # Bot yuborgan xabar
    await asyncio.sleep(60)  # 60 soniya kutish
    await sent_message.delete()

# Adminlarni tekshirish uchun yordamchi funksiya
async def is_admin(chat_id: int, user_id: int) -> bool:
    admins = await bot.get_chat_administrators(chat_id)
    return any(admin.user.id == user_id for admin in admins)


@dp.message(Command('set_title'))
async def set_group_title(message: Message):
    if await is_admin(message.chat.id, message.from_user.id):
        title = message.text.split(maxsplit=1)[1]
        await message.chat.set_title(title)
        await message.answer(f"Guruh nomi {title} qilib o'zgartirildi. ✅")
    else:
        await message.answer("⛔ Sizda bu kommandani bajarish uchun huquq yo'q!")

# Guruh linkini o'zgartirish
@dp.message(Command('set_link'))
async def set_group_link(message: Message):
    if await is_admin(message.chat.id, message.from_user.id):
        try:
            # Yangi taklif linkini yaratish
            new_link = await bot.export_chat_invite_link(message.chat.id)
            await message.answer(f"Guruh linki muvaffaqiyatli yangilandi. 🔗 Yangi link: {new_link}")
        except Exception as e:
            await message.answer(f"⚠️ Xatolik yuz berdi: {str(e)}")
    else:
        await message.answer("⛔ Sizda bu kommandani bajarish uchun huquq yo'q!")


# Foydalanuvchini ban qilish
@dp.message(F.new_chat_member)
async def new_member(message:Message):
    user = message.new_chat_member.get("first_name")
    await message.answer(f"{user} Guruhga xush kelibsiz!")
    await message.delete()

@dp.message(F.left_chat_member)
async def new_member(message:Message):
    # print(message.new_chat_member)
    user = message.left_chat_member.full_name
    await message.answer(f"{user} Xayr!")
    await message.delete()

@dp.message(and_f(F.reply_to_message,F.text=="/ban"))
async def ban_user(message:Message):
    user_id =  message.reply_to_message.from_user.id
    await message.chat.ban_sender_chat(user_id)
    await message.answer(f"{message.reply_to_message.from_user.first_name} guruhdan chiqarib yuborilasiz.")

@dp.message(and_f(F.reply_to_message,F.text=="/unban"))
async def unban_user(message:Message):
    user_id =  message.reply_to_message.from_user.id
    await message.chat.unban_sender_chat(user_id)
    await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga qaytishingiz mumkin.")

from time import time
@dp.message(and_f(F.reply_to_message,F.text=="/mute"))
async def mute_user(message:Message):
    user_id =  message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=False)

    until_date = int(time()) + 300 # 1minut guruhga yoza olmaydi
    await message.chat.restrict(user_id=user_id,permissions=permission,until_date=until_date)
    await message.answer(f"{message.reply_to_message.from_user.first_name} 5 minutga blocklandingiz")

@dp.message(and_f(F.reply_to_message,F.text=="/unmute"))
async def unmute_user(message:Message):
    user_id =  message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=True)
    await message.chat.restrict(user_id=user_id,permissions=permission)
    await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga yoza olasiz")

user_warnings = {}

from time import time
xaqoratli_sozlar = {"tentak","jinni", "to'poy", "axmoq", "iplos", "maraz", "ahmoq"}
@dp.message(F.chat.func(lambda chat: chat.type == "supergroup"), F.text)
async def tozalash(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.lower()

    # Agar foydalanuvchi oldin so‘kingan bo‘lsa, uning ogohlantirish sonini oshiramiz
    if user_id not in user_warnings:
        user_warnings[user_id] = 0

    # Xabarni xaqoratli so‘zlarga tekshiramiz
    for soz in xaqoratli_sozlar:
        if soz in text:
            user_warnings[user_id] += 1  # Ogohlantirishni oshiramiz
            await message.delete()  # So‘kinish xabarini o‘chirib tashlaymiz

            if user_warnings[user_id] == 1:
                await message.answer(f"{message.from_user.mention_html()} ❗ Bu birinchi ogohlantirish! Guruhda so‘kinmang.")
            elif user_warnings[user_id] == 2:
                until_date = int(time()) + 600  # 10 daqiqaga mute
                permission = ChatPermissions(can_send_messages=False)
                await message.chat.restrict(user_id=user_id, permissions=permission, until_date=until_date)
                await message.answer(f"{message.from_user.mention_html()} 🔇 10 daqiqaga yozish huquqingiz cheklandi!")
            elif user_warnings[user_id] >= 3:
                await message.chat.ban_sender_chat(user_id)  # Butun umrga ban
                await message.answer(f"{message.from_user.mention_html()} 🚫 Siz guruhdan butunlay bloklandingiz!")
            
            break