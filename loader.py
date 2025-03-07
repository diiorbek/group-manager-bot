from aiogram import Bot, Dispatcher
from data import config
from baza.sqlite import Database
from aiogram.enums import ParseMode
from aiogram import F


ADMINS = config.ADMINS
TOKEN = config.BOT_TOKEN
CHANNELS = config.CHANNELS


bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
db = Database(path_to_db="main.db")
dp = Dispatcher()

private = F.chat.func(lambda chat: chat.type == "private")
group = F.chat.func(lambda chat: chat.type == "group")  
supergroup = F.chat.func(lambda chat: chat.type == "supergroup")
channel = F.chat.func(lambda chat: chat.type == "channel")
