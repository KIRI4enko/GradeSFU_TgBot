import requests
import telebot
import s_taper
from s_taper.consts import INT, KEY, TEXT
from bs4 import BeautifulSoup
from telebot.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup
import json
import datetime

scheme = {
    'user_id': INT + KEY,
    'token': INT,
    'updated_time': TEXT
}
users = s_taper.Taper('users', 'users.db').create_table(scheme)

token = '7669708347:AAH0YG5NHjKToWsVwTqKGVpcksdumwyLbVo'

bot = telebot.TeleBot(token)
clear = ReplyKeyboardRemove()
kb_menu = ReplyKeyboardMarkup(True, False)
kb_menu.row('/token', '/help')
def get_token(url: str):
    l = url.find('token') + 6
    r = url.find('&', l)
    return url[l:r]


@bot.message_handler(['start'])
def start(msg: Message):
    bot.send_message(msg.chat.id, f"Привет, {msg.from_user.first_name}!\n"
                                  f"@Kirill_kin - это мой папа! Если встретишь какие-либо ошибки, пиши ему. Спасибо!\n"
                                  f"Для работы мне нужна ссылка на ленту событий. Чтобы ее ввести, используй команду /token.\n"
                                  f"Если не знаешь, где его найти, напиши /help. Там вся инструкция", reply_markup=kb_menu)


@bot.message_handler(['help'])
def help(msg: Message):
    photo = open('help1.PNG', 'rb')
    bot.send_photo(msg.chat.id, photo,
                   'Инструкция:\n'
                   '1) Войдя в свой профиль, вы попадаете на главную страницу, '
                   'где необходимо выбрать вкладку "История событий"', reply_markup=clear)

    photo = open('help2.PNG', 'rb')
    bot.send_photo(msg.chat.id, photo,
                   '2) Далее необходимо нажать на кнопку "подписаться на ленту"')

    photo = open('help3.PNG', 'rb')
    bot.send_photo(msg.chat.id, photo,
                   '3) Дальше должно появиться модальное окно, где необходимо нажать "OK". '
                   'Теперь ссылка находиться в буфере обмена', reply_markup=kb_menu
                   )
    photo.close()


@bot.message_handler(['token'])
def token(msg: Message):
    bot.send_message(msg.chat.id, 'Введите ссылку здесь...', reply_markup=clear)
    bot.register_next_step_handler(msg, token2)


def token2(msg: Message):
    if 'token' in msg.text and 'recordbook' in msg.text and 'semester' in msg.text:
        users.write([msg.chat.id, msg.text, datetime.datetime.now().timestamp()])
        bot.send_message(msg.chat.id, "Я запомнил твою ссылку)", reply_markup=kb_menu)
    else:
        bot.send_message(msg.chat.id, "Мне не понравилось, как выглядит эта ссылка. Попробуйте еще раз", reply_markup=kb_menu)

    print(users.read_all())


@bot.message_handler(['info'])
def info(msg: Message):
    url = users.read('user_id', msg.chat.id)
    if not url:
        bot.send_message(msg.chat.id, 'Произошла ошибка... Скорее всего вы просто не ввели ссылку')
        return
    token = get_token(users.read('user_id', msg.chat.id)[1])
    r = requests.get('http://grade.sfedu.ru/api/v1/student', {'token': token})
    if r:
        js = json.loads(BeautifulSoup(r.text, 'lxml').find('p').text)['response']
        res = 'Баллы по дисциплинам:\n'
        for d in js['Disciplines']:
            res += f'"{d['SubjectName']}": {d['Rate']}/{d['MaxCurrentRate']}\n'

        bot.send_message(msg.chat.id, res)

        if 'None/0' in res:
            bot.send_message(msg.chat.id,
                         F'Если вы видите "None/0", не бойтесь. Может быть, карточка дисциплины еще не создана')
    else:
        bot.send_message(msg.chat.id, f'Произошла ошибка. Результат запроса {r.status_code}')


bot.infinity_polling()
