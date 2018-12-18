import math
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import requests
import re

last_film = {}
imdb_links = {}

TOKEN = '764982895:AAG4Lt2sYm9HguSdX0lHeztTp_I7ZqrgxaE'


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def gcd(x, y):
    if x == 0:
        return y
    return gcd(y % x, x)

def euler_function(n):
    num = 1 # initialization, because there's always a 1
    for _ in range(2, n):
        if gcd(n, _) == 1:
            num += 1
    return num

def fast_pow(x, n, mod=0):
    if n < 0:
        return fast_pow(1/x, -n, mod=mod)
    if n == 0:
        return 1
    if n == 1:
        if mod == 0:
            return x
        else:
            return x % mod
    if n % 2 == 0:
        if mod == 0:
            return fast_pow(x * x,  n / 2, mod=mod)
        else:
            return fast_pow(x * x,  n / 2, mod=mod) % mod
    else:
        if mod == 0:
            return x * fast_pow(x * x, (n - 1) / 2, mod=mod)
        else:
            return x * fast_pow(x * x, (n - 1) / 2, mod=mod) % mod


def discrete_log(a, b, p):
    """
    In this function we are using an assumption that p is a prime number
    """
    H = math.ceil(math.sqrt(p - 1))

    hash_table = {fast_pow(a, i, p): i for i in range(H)}

    c = fast_pow(a, H * (p - 2), p)

    for j in range(H):
        x = (b * fast_pow(c, j, p)) % p
        if x in hash_table:
            return j * H + hash_table[x]

    return None



@dp.message_handler(commands=['start'], commands_prefix='!/')
async def process_start_command(message: types.Message):
    await message.reply("Это бот показывает работу некоторых функций")


@dp.message_handler(commands=['help'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    await bot.send_message(message.from_user.id, "Выдаю результаты некоторых функций \n \
                        /poster -- постер данного фильма \n \
                        /watch -- еще места, где посмотреть фильм \n \
                        /rating -- рейтинг фильма по версии imdb \n \
                        /wiki -- данный фильм на википедии \n \
                        /imdb -- данный фильм на imdb")


@dp.message_handler(commands=['fast_pow'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[8:]
    s = text.split()
    if len(s) == 2:
        a, b = s
        a, b = int(a), int(b)
        result = fast_pow(a, b)
    else:
        a, b, m = s
        a, b, m = int(a), int(b), int(m)
        result = fast_pow(a, b, m)
    await bot.send_message(message.from_user.id, result)

@dp.message_handler(commands=['echo'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    await bot.send_message(message.from_user.id, text)


@dp.message_handler()
async def film_info(msg: types.Message):

    text = msg.text
    await bot.send_message(msg.from_user.id, 'Я тебя не понимаю')


if __name__ == '__main__':
    executor.start_polling(dp)