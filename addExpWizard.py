import telebot
from telebot.storage import StateMemoryStorage
from telebot import types
from telebot.types import ReplyKeyboardRemove

from bot import bot
from cmdparser import get_cmd
from controller import add_expense, get_users


def description_callback(message, data):
    print('description_callback', message.text)
    data['description'] = message.text[1:]
    print(data)

    resp = add_expense(message.chat.id,
        get_cmd(data['amount'],
                data['description'],
                data['ultype'],
                data['whom']),
        data['who'])

    bot.reply_to(message, resp,
                 parse_mode='HTML',
                 reply_markup=None)

def get_int_amount(s):
    s = s.replace('/','')
    try:
        return int(s)
    except ValueError:
        return None

def amount_callback(message, data):
    print('amount_callback', message.text)
    amnt = get_int_amount(message.text)
    if amnt:
        data['amount'] = amnt
        msg = bot.send_message(message.chat.id, 'Введите описание траты (через /):')
        bot.register_next_step_handler(msg, description_callback, data)
    else:
        ask_amount_step(data, message, 'необходимо ввести число\n')

def whom_callback(message, data):
    print('whom_callback', message.text)

    if 'whom' not in data:
        data['whom'] = []

    if message.text == 'Хватит' or message.text == 'На всех':
        if message.text == 'Хватит':
            data['ultype'] = '>'
        else:
            data['ultype'] = ''
            data['whom'] = []

        ask_amount_step(data, message)

    else:
        data['whom'].append(message.text)
        msg = bot.send_message(message.chat.id, 'На кого делим сумму:\n ' + ' '.join(data['whom']) + '\nДобавить еще')#, reply_markup=markup
        bot.register_next_step_handler(msg, whom_callback, data)


def ask_amount_step(data, message, txt=''):
    msg = bot.send_message(message.chat.id, txt + 'Сумма (через <code>/</code>):',
                           reply_markup=ReplyKeyboardRemove(),
                           parse_mode='HTML')
    bot.register_next_step_handler(msg, amount_callback, data)


def who_callback(message, data):
    print('who_callback', message.text)
    data['who'] = message.text

    markup = get_users(message, False)
    msg = bot.send_message(message.chat.id, 'На кого делим сумму:', reply_markup=markup)
    bot.register_next_step_handler(msg, whom_callback, data)

# команда для запуска визарда для добавления расхода
@bot.message_handler(commands=['add'])
def start_message(message):
    raise Exception
    markup = get_users(message, True)

    msg = bot.send_message(message.chat.id, 'Выберите, кто заплатил?', reply_markup=markup)
    # объект для хранения ввода пользователя на всех шагах
    data = {}
    bot.register_next_step_handler(msg, who_callback, data)
