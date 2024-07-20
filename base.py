import telebot
from random import choice
from telebot import types
import sqlite3

with open('../hidden/TOKEN.txt') as ToKEN:
    TOKEN = ToKEN.readline()
    bot = telebot.TeleBot(TOKEN)

password = None


def generator(punc=True):
    global password
    digits = '0123456789'
    uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lowercase = 'abcdefghijklmnopqrstuvwxyz'
    punctuation = '!#$%&*+-=?@^_'
    ally = ''
    match punc:
        case True:
            ally = digits + uppercase + lowercase + punctuation
        case False:
            ally = digits + uppercase + lowercase
    chars = ''
    pwd_length = 30
    chars += ally
    password = ''
    for i in range(pwd_length):
        password += choice(chars)
    return password


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Хай, я храню и создаю пароли')
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEHASJmmSEaDHXdMUw7kahmUwEjeqW01AACvj0AAh9FKElNm2mLCcUj0TUE')


@bot.message_handler(commands=['view'])
def view(message):
    conn = sqlite3.connect('bsd.sql')
    cur = conn.cursor()
    if cur.execute("SELECT COUNT(*) FROM passwords").fetchone()[0] > 0:
        cur.execute('SELECT * FROM passwords WHERE user_id=?', (message.from_user.id,))
        pswds = cur.fetchall()
        info = ''
        for i in pswds:
            info += f'ID {i[0]}:    {i[1]} - {i[2]} \n'
        bot.send_message(message.chat.id, info)
        cur.close()
        conn.close()
    else:
        bot.send_message(message.chat.id, "Список паролей пуст")


@bot.message_handler(commands=['psw'])
def on_click2(message):
    mark = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.InlineKeyboardButton('Со СпецСимволами', callback_data="answer1")
    item2 = types.InlineKeyboardButton('Без СпецСимволов', callback_data="answer2")
    mark.row(item1, item2)
    bot.send_message(message.chat.id, 'Выберите параметр', reply_markup=mark)
    bot.register_next_step_handler(message, flag2)


def flag2(message):
    punctuation = False
    if message.text == 'Со СпецСимволами':
        punctuation = True
    elif message.text == 'Без СпецСимволов':
        punctuation = False
    else:
        return on_click2(message)
    bot.send_message(message.chat.id, 'Впишите название сервиса и будет произведена генерация пароля:')
    bot.register_next_step_handler(message, create, punctuation)


def create(message, punctuation):
    global password
    conn = sqlite3.connect('bsd.sql', check_same_thread=False)
    cur = conn.cursor()
    name = message.text
    password = generator(punctuation)
    cur.execute('INSERT INTO passwords (name, password, user_id) VALUES (?, ?, ?)',
                (name, password, message.from_user.id))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Информация добавлена')


@bot.message_handler(commands=['change'])
def change_psw(message):
    conn = sqlite3.connect('bsd.sql')
    cur = conn.cursor()
    if cur.execute("SELECT COUNT(*) FROM passwords").fetchone()[0] > 0:
        mark = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Вручную', callback_data='manual')
        button2 = types.InlineKeyboardButton('Авто', callback_data='auto')
        mark.add(button1, button2)
        bot.send_message(message.chat.id, 'Вы можете вручную поменять пароль или сгенерировать новый :',
                         reply_markup=mark)
    else:
        bot.send_message(message.chat.id, "Список паролей пуст")
    cur.close()
    conn.close()


@bot.callback_query_handler(func=lambda callback: True)
def callbackon(callback):
    if callback.data == 'manual':
        bot.send_message(callback.message.chat.id, 'Введите ID поля (чтобы увидеть ID используйте команду view)')
        bot.register_next_step_handler(callback.message, emanuale)
    elif callback.data == 'auto':
        on_click(callback.message)


def emanuale(message):
    idm = message.text
    conn = sqlite3.connect('bsd.sql')
    cur = conn.cursor()
    if cur.execute("SELECT * FROM passwords WHERE id=?", (idm,)).fetchone()[3] == message.from_user.id:
        bot.send_message(message.chat.id, 'Введите новый пароль:')
        bot.register_next_step_handler(message, set_newm, idm)
    else:
        bot.send_message(message.chat.id, 'Такого пароля не существует')
    cur.close()
    conn.close()


def set_newm(message, idm):
    conn = sqlite3.connect('bsd.sql')
    cur = conn.cursor()
    pswrd = message.text
    cur.execute(f'UPDATE passwords SET password=? WHERE id=?', (pswrd, idm))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Информация обновлена')


def on_click(message):
    mark = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.InlineKeyboardButton('Со СпецСимволами', callback_data="answer1")
    item2 = types.InlineKeyboardButton('Без СпецСимволов', callback_data="answer2")
    mark.row(item1, item2)
    bot.send_message(message.chat.id, 'Выберите параметр', reply_markup=mark)
    bot.register_next_step_handler(message, flag)


def flag(message):
    punctuation = False
    if message.text == 'Со СпецСимволами':
        punctuation = True
    elif message.text == 'Без СпецСимволов':
        punctuation = False
    else:
        return on_click(message)
    bot.send_message(message.chat.id, 'Введите ID поля (чтобы увидеть ID используйте команду view)')
    bot.register_next_step_handler(message, set_newa, punctuation)


def set_newa(message, punctuation):
    conn = sqlite3.connect('bsd.sql')
    cur = conn.cursor()
    idm = message.text
    if cur.execute("SELECT * FROM passwords WHERE id=?", (idm,)).fetchone()[3] == message.from_user.id:
        pswrd = generator(punctuation)
        cur.execute(f'UPDATE passwords SET password=? WHERE id=?', (pswrd, idm))
        conn.commit()
        bot.send_message(message.chat.id, 'Информация обновлена')
    else:
        bot.send_message(message.chat.id, 'Такого пароля не существует')
    cur.close()
    conn.close()


@bot.message_handler(commands=['delete'])
def process_message(message):
    bot.send_message(message.chat.id, 'Введите ID поля (чтобы увидеть ID используйте команду view)')
    bot.register_next_step_handler(message, delete)


def delete(message):
    conn = sqlite3.connect('bsd.sql')
    cur = conn.cursor()
    if cur.execute("SELECT COUNT(*) FROM passwords").fetchone()[0] > 0:
        idm = message.text
        if cur.execute("SELECT * FROM passwords WHERE id=?", (idm,)).fetchone()[3] == message.from_user.id:
            cur.execute('DELETE FROM passwords WHERE id=?', (idm,))
            conn.commit()
            bot.send_message(message.chat.id, f'Пароль с ID {idm} удален')
        else:
            bot.send_message(message.chat.id, 'Такого пароля не существует')
    else:
        bot.send_message(message.chat.id, "Список паролей пуст")
    cur.close()
    conn.close()


bot.polling(none_stop=True)
