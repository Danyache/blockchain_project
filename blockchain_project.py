import math
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import requests
import re
from random import randint
from functools import reduce

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

def crt(n, a):
    sum = 0
    prod = reduce(lambda a, b: a*b, n)
    for n_i, a_i in zip(n, a):
        p = prod / n_i
        sum += a_i * mul_inv(p, n_i) * p
    return sum % prod

def mul_inv(a, b):
    b0 = b
    x0, x1 = 0, 1
    if b == 1: return 1
    inv = eea(a,b)[0]
    if inv < 1: inv += b
    return inv

def eea(a,b):
    if b==0:return (1,0)
    (q,r) = (a//b,a%b)
    (s,t) = eea(b,r)
    return (t, s-(q*t))

def find_inverse(x,y):
    inv = eea(x,y)[0]
    if inv < 1: inv += y
    return inv


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
            
def egcd(a, b):
    if (a == 0):
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def is_prime(num, test_count):
    if num == 1:
        return False
    if test_count >= num:
        test_count = num - 1
    for x in range(test_count):
        val = randint(1, num - 1)
        if pow(val, num-1, num) != 1:
            return False
    return True

def generate_big_prime(n, test_count=1000):
    found_prime = False
    while not found_prime:
        p = randint(2**(n-1), 2**n)
        if is_prime(p, test_count):
            return p
        
def generate_modulo(bitlen, tc=1000):       
    p = generate_big_prime(bitlen//2, tc)                          
    q = 1
    n = p * q  
    while (math.ceil(math.log(n, 2)) != bitlen):
        q = generate_big_prime(bitlen - bitlen//2, tc)
        n = p * q

    return  n, (p-1)*(q-1)

def rsa_generate_keys(bitlen, tc=1000):
    '''
    inputs:
    bitlen - bitwise size of the keys
    tc - number of iterations for cheking the primality
    returns:
    private_key: (modulo, exponent), public_key: (modulo, exponent)
    
    '''
    p1 = generate_big_prime(bitlen, tc)
    p2 = generate_big_prime(bitlen, tc)
    n = p1 * p2
    phi = (p1 - 1)*(p2 - 1)
    for i in range(3, phi):
        if gcd(i, phi) == 1:
            e = i
            break
    d = find_inverse(e, phi)
    return (n, d), (n, e)

def rsa_encrypt(public_key, message, modulo):
    return fast_pow(message, public_key, modulo)

def rsa_decrypt(private_key, message, modulo):
    return fast_pow(message, private_key, modulo)

def rsa_sign(private_key, h, modulo):
    '''
    h - hash
    '''
    return fast_pow(h, private_key, modulo)

def rsa_check(public_key, h, g, modulo):
    '''
    h - received hash value
    g - computed hash value
    '''
    return fast_pow(h, public_key, modulo) == g

""" 
Дальше идут команды для бота
"""

@dp.message_handler(commands=['rsa_gen_keys'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[13:]
    s = text.split()
    
    bitlen = int(s[0])
    
    result = rsa_generate_keys(bitlen)
    
    await bot.send_message(message.from_user.id, 'Private key is {}'.format(result[0]))
    await bot.send_message(message.from_user.id, 'Public key is {}'.format(result[1]))

@dp.message_handler(commands=['rsa_encrypt'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[12:]
    s = text.split()
    
    pub, m, mod = s
    pub, m, mod = int(pub), int(m), int(mod)
    
    result = rsa_encrypt(pub, m, mod)
    await bot.send_message(message.from_user.id, result)

@dp.message_handler(commands=['rsa_decrypt'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[12:]
    s = text.split()
    priv, m, mod = s
    priv, m, mod = int(priv), int(m), int(mod)

    result = rsa_decrypt(priv, m, mod)
    await bot.send_message(message.from_user.id, result)

@dp.message_handler(commands=['rsa_sign'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[9:]
    s = text.split()
    p, h, m = s
    p, h, m = int(p), int(h), int(m)

    result = rsa_sign(p, h, m)
    await bot.send_message(message.from_user.id, result)

@dp.message_handler(commands=['rsa_check'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[10:]
    s = text.split()
    p, h, g, m = s
    p, h, g, m = int(p), int(h), int(g), int(m)

    result = rsa_check(p, h, g, m)
    await bot.send_message(message.from_user.id, str(result))


@dp.message_handler(commands=['start'], commands_prefix='!/')
async def process_start_command(message: types.Message):
    await message.reply("Это бот показывает работу некоторых функций")


@dp.message_handler(commands=['help'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    await bot.send_message(message.from_user.id, "\
        Выдаю результаты некоторых функций \n \
        Все аргементы данных функций вводятся после команды подряд через пробел \n \
        /fast_pow(x, n, mod=None) -- возвожу число в степень методом fast powering \n \
        /disc_log(a, b, p) -- нахожу логарифм для двух чисел в поле вычетов простого числа p \n \
        /euler(x) -- нахожу значение функции Эйлера для заданного числа \n \
        /crt(array_x, array_n) -- решаю задачу китайской теоремы об остатках (первый и второй массивы вводятся подряд через пробел) \n \
        /find_inverse(x, mod) -- обобщенный алгоритм евклида \n \
        /rsa_gen_keys(bitlen) -- сгенерировать ключи \n \
        /rsa_encrypt(e, message, n) -- encrypt message \n \
        /rsa_decrypt(d, message, n) -- decrypt message \n \
        /rsa_sign(d, h, n) -- create sign \n \
        /rsa_check(e, h, g, n) -- check sign \n ")



@dp.message_handler(commands=['fast_pow'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[9:]
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

@dp.message_handler(commands=['disc_log'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[9:]
    s = text.split()
    a, b, p = s
    a, b, p = int(a), int(b), int(p)
    result = discrete_log(a, b, p)
    await bot.send_message(message.from_user.id, result)

@dp.message_handler(commands=['euler'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[6:]
    s = text.split()
    a = int(s[0])
    result = euler_function(a)
    await bot.send_message(message.from_user.id, result)

@dp.message_handler(commands=['crt'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[4:]
    s = text.split()
    length = len(s)
    n = []
    a = []
    for i in range(int(length/2)):
        n.append(int(s[i]))
        a.append(int(s[i+int(length/2)]))

    result = crt(n, a)

    await bot.send_message(message.from_user.id, result)

@dp.message_handler(commands=['find_inverse'], commands_prefix='!/')
async def process_help_command(message: types.Message):
    text = message.text
    text = text[13:]
    s = text.split()
    a, b = s
    a, b = int(a), int(b)
    result = find_inverse(a, b)
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