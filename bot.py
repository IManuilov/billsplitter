import threading

import telebot
from telebot.storage import StateMemoryStorage
from telebot import types
from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, BotCommand

import addExpWizard
from Config import config
from cmdparser import get_cmd
from controller import add_user_button, del_button, add_expense_cmd, del_cmd, clear_cmd, get_users, add_expense
from database import loadExpenses, saveExpenses


state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.TELEBOT_TOKEN, state_storage=state_storage)

bot.set_my_commands([
    BotCommand(command='/add', description='добавить траты'),
    BotCommand(command='/me', description='добавить пользователя'),
    BotCommand(command='/start', description='начать с нуля'),
    BotCommand(command='/del', description='удаление записей'),
]);


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = clear_cmd(message)

    bot.send_message(message.chat.id, 'Начали с нуля. Нажмите кнопку все кто учавствует в разделе расходов', reply_markup=markup)

    # bot.reply_to(message, "Привет! Нажми кнопку Menu, чтобы открыть меню.", reply_markup=create_menu_keyboard())



# команда для запуска визарда для добавления расхода
@bot.message_handler(commands=['add'])
def start_message(message):
    # raise Exception
    markup = get_users(message, True)

    msg = bot.send_message(message.chat.id, 'Выберите, кто заплатил?', reply_markup=markup)
    # объект для хранения ввода пользователя на всех шагах
    data = {}
    bot.register_next_step_handler(msg, who_paid_callback, data)

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

def recipients_callback(message, data):
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
        bot.register_next_step_handler(msg, recipients_callback, data)


def ask_amount_step(data, message, txt=''):
    msg = bot.send_message(message.chat.id, txt + 'Сумма (через <code>/</code>):',
                           reply_markup=ReplyKeyboardRemove(),
                           parse_mode='HTML')
    bot.register_next_step_handler(msg, amount_callback, data)


def who_paid_callback(message, data):
    print('who_callback', message.text)
    data['who'] = message.text

    markup = get_users(message, False)
    msg = bot.send_message(message.chat.id, 'На кого делим сумму:', reply_markup=markup)
    bot.register_next_step_handler(msg, recipients_callback, data)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, config.HELP_MSG, parse_mode='HTML')


# remove expense script
@bot.message_handler(commands=['del'])
def del_message(message):
    markup = del_cmd(message)

    bot.send_message(message.chat.id, 'удаление', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "addme":
        msg = add_user_button(call)

        bot.send_message(call.message.chat.id, msg, parse_mode='HTML')

    elif call.data.startswith("del"):

        bot.edit_message_text(call.message.text + '\n\nУдален расход',
                              chat_id=call.message.chat.id,
                              message_id=call.message.id,
                              reply_markup=None)

        tables = del_button(call)

        bot.send_message(call.message.chat.id, tables, parse_mode='HTML')
    elif call.data.startswith("usr"):
        print(call.data)


# @bot.message_handler(content_types=['text'])
def get_text_messages(message):
    print('text')
    resp = add_expense_cmd(message)

    # markup = types.InlineKeyboardMarkup()
    # for i, it in enumerate(expense.userSet()):
    #     markup.add(types.InlineKeyboardButton(text=str(it), callback_data='usr' + it))
    markup = None

    bot.reply_to(message, resp,
                 parse_mode='HTML',
                 reply_markup=markup)


from flask import Flask

app = Flask(__name__)

@app.route("/health")
def index():
    return "Congratulations, it's a web app!"

# class FlaskThread(threading.Thread):
#     def run(self) -> None:
#         app.run(host="0.0.0.0", port=9086)


# class TelegramThread(threading.Thread):
#     def run(self) -> None:
#         bot.polling(none_stop=True)

if __name__ == "__main__":
    # flask_thread = FlaskThread()
    # flask_thread.start()

    bot.polling(none_stop=True)