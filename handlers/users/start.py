from aiogram.types import Message
from aiogram import F
from loader import dp, db, bot, CHANNELS, ADMINS
from aiogram.filters import CommandStart, Command, and_f
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import time
from aiogram.types import Message, ChatPermissions
import logging
import asyncio
from filters.admin import IsBotAdminFilter
import sqlite3
from matplotlib import pyplot as plt
from aiogram.types import FSInputFile

logging.basicConfig(level=logging.INFO)

# Ma'lumotlar bazasiga ulanish
conn = sqlite3.connect('group_stats.db')
cursor = conn.cursor()

# Jadval yaratish
cursor.execute('''
CREATE TABLE IF NOT EXISTS group_stats (
    id INTEGER PRIMARY KEY,
    added INTEGER DEFAULT 0,
    left INTEGER DEFAULT 0,
    added_by TEXT
)
''')
conn.commit()

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
    new_users = message.new_chat_members
    inviter = message.from_user  # Kim qo‘shganini tekshirish
    await message.delete()
    for user in new_users:
        cursor.execute('UPDATE group_stats SET added = added + 1 WHERE id = 1')
        conn.commit()
        
        if inviter and inviter.id != user.id:  # Agar boshqasi qo‘shgan bo‘lsa
            cursor.execute('SELECT added_by FROM group_stats WHERE id = 1')
            added_by = cursor.fetchone()[0]
            added_by_dict = eval(added_by) if added_by else {}
            added_by_dict.setdefault(inviter.id, 0)
            added_by_dict[inviter.id] += 1
            cursor.execute('UPDATE group_stats SET added_by = ? WHERE id = 1', (str(added_by_dict),))
            conn.commit()
        
        welcome_message = f"🎉 {user.full_name}, guruhimizga xush kelibsiz! 😊"
        sent_message = await message.answer(welcome_message)
        await asyncio.sleep(60)
        await sent_message.delete()

# Guruhdan a'zo chiqib ketganda
@dp.message(F.left_chat_member)
async def member_left(message: Message):
    user = message.left_chat_member  # Chiqib ketgan foydalanuvchi
    await message.delete()
    if user:
        cursor.execute('UPDATE group_stats SET left = left + 1 WHERE id = 1')
        conn.commit()
        
        goodbye_message = f"😢 {user.full_name}, siz bilan xayrlashamiz! 🌙\nYana qaytib kelishingizni kutamiz! 🙌"
        sent_message = await message.answer(goodbye_message)
        await asyncio.sleep(60)
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
@dp.message(and_f(F.reply_to_message, F.text == "/ban"))
async def ban_user(message: Message):
    user_id = message.reply_to_message.from_user.id
    await message.chat.ban_sender_chat(user_id)
    await message.answer(f"{message.reply_to_message.from_user.first_name} guruhdan chiqarib yuborilasiz.")

@dp.message(and_f(F.reply_to_message, F.text == "/unban"))
async def unban_user(message: Message):
    user_id = message.reply_to_message.from_user.id
    await message.chat.unban_sender_chat(user_id)
    await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga qaytishingiz mumkin.")

from time import time

@dp.message(and_f(F.reply_to_message, F.text == "/mute"))
async def mute_user(message: Message):
    user_id = message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=False)

    until_date = int(time()) + 300  # 1minut guruhga yoza olmaydi
    await message.chat.restrict(user_id=user_id, permissions=permission, until_date=until_date)
    await message.answer(f"{message.reply_to_message.from_user.first_name} 5 minutga blocklandingiz")

@dp.message(and_f(F.reply_to_message, F.text == "/unmute"))
async def unmute_user(message: Message):
    user_id = message.reply_to_message.from_user.id
    permission = ChatPermissions(can_send_messages=True)
    await message.chat.restrict(user_id=user_id, permissions=permission)
    await message.answer(f"{message.reply_to_message.from_user.first_name} guruhga yoza olasiz")

user_warnings = {}

from time import time
xaqoratli_sozlar = {"tentak", "jinni", "to'poy", "axmoq", "ahmoq", "tupoy", "lanati"}

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

def create_stat_chart(added, left):
    # Statistika diagrammasi (dumaloq)
    labels = ["Qo'shilganlar", "Chiqib ketganlar"]
    values = [added, left]
    colors = ['#4CAF50', '#F44336']
    
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90, shadow=True)
    ax.set_title("Guruh Statistikalari", fontsize=14)
    
    # Diagrammani PNG fayl sifatida saqlash
    file_path = 'group_stats_pie.png'
    plt.savefig(file_path, format='PNG')
    plt.close(fig)
    
    return file_path

# Dastlabki ma'lumotlarni yaratish
def initialize_stats():
    cursor.execute('SELECT * FROM group_stats WHERE id = 1')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO group_stats (id, added, left, added_by) VALUES (1, 0, 0, "{}")')
        conn.commit()

# Dastlabki ma'lumotlarni yaratishni ishga tushirish
initialize_stats()

# Statistika komandasi
@dp.message(F.text == "/stats", IsBotAdminFilter(ADMINS))
async def group_statistics(message: Message):
    cursor.execute('SELECT added, left, added_by FROM group_stats WHERE id = 1')
    stats = cursor.fetchone()
    
    # Agar ma'lumotlar mavjud bo'lmasa, dastlabki ma'lumotlarni yaratamiz
    if not stats:
        initialize_stats()
        cursor.execute('SELECT added, left, added_by FROM group_stats WHERE id = 1')
        stats = cursor.fetchone()
    
    total_added = stats[0]
    total_left = stats[1]
    added_by_dict = eval(stats[2]) if stats[2] else {}

    # Diagrammani yaratish va faylga saqlash
    chart_file_path = create_stat_chart(total_added, total_left)
    
    growth = 0
    if total_added > 0:
        growth = ((total_added - total_left) / total_added) * 100  # O‘sish foizi

    # Eng ko‘p odam qo‘shgan foydalanuvchilar
    added_by_list = []
    max_adder = None
    max_count = 0
    
    for user_id, count in added_by_dict.items():
        try:
            chat_member = await bot.get_chat(user_id)  # Foydalanuvchi ismini olish
            full_name = chat_member.full_name
            added_by_list.append(f"👤 <a href='tg://user?id={user_id}'>{full_name}</a>: {count} kishi")

            if count > max_count:
                max_adder = (user_id, full_name, count)

        except Exception as e:
            print(f"Xatolik: {e}")  # Xato chiqmasligi uchun

    added_by_text = "\n".join(added_by_list) if added_by_list else "❌ Hech kim odam qo‘shmagan."

    # Eng ko‘p odam qo‘shgan foydalanuvchi
    top_adder_text = "❌ Ma’lumot yo‘q."
    if max_adder:
        top_adder_text = f"🥇 <a href='tg://user?id={max_adder[0]}'>{max_adder[1]}</a> {max_adder[2]} kishi qo‘shgan!"

    # Statistika matni
    stats_message = (
        f"📊 <b>Guruh statistikasi:</b>\n"
        f"👥 Jami qo‘shilganlar: {total_added}\n"
        f"🚪 Jami chiqib ketganlar: {total_left}\n"
        f"📈 O‘sish foizi: {growth:.2f}%\n\n"
        f"🏆 <b>Eng ko‘p odam qo‘shgan:</b>\n{top_adder_text}\n\n"
        f"👤 <b>Eng ko‘p odam qo‘shganlar:</b>\n{added_by_text}"
    )

    # Statistika va diagrammani yuborish
    await message.answer_photo(photo=FSInputFile(chart_file_path), caption=stats_message, parse_mode="HTML")