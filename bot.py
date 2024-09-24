import threading

import telebot
from telebot.storage import StateMemoryStorage
from telebot import types
from telebot.types import ReplyKeyboardRemove

from Config import config
from cmdparser import get_cmd
from controller import add_user_button, del_button, add_expense_cmd, del_cmd, clear_cmd, get_users, add_expense
from database import loadExpenses, saveExpenses


state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.TELEBOT_TOKEN, state_storage=state_storage)


# печатать сразу расшифровку, добавленного расхода, кто сколько должен по не му автору

# db best practice
# help
# показывать список команд при /
# удаление кнопки
# ругаться на несуествующих юзеров
# ругаться на неформат
# подумать над ситуациий с новым юзером после того как расходы уже добавлены

# +конфиг
# +взаиморасчеты
# +расход не на всех
# +embedded db scripts
# +group by date
# +format float
# + регистрация юзеров

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = clear_cmd(message)

    bot.send_message(message.chat.id, 'Начали с нуля. Нажмите кнопку все кто учавствует в разделе расходов', reply_markup=markup)


help_msg = """
добавить в группу бот и выполнить команду
<code>/start</code>
после чего все должны нажать кнопку "Я в деле"

далее могут быть такие сценарии:

я купил в магазине продуктов на всех:
<code>/4000 продукты</code>

я купил алкоголь на всех, но друг№1 его пить не будет:
<code>/2500 алкоголь - @drug1</code>
(после символа '-' (минус) перечисляем через пробел никнеймы тех кого исключить)

я оплатил в ресторане счет за себя и 2х товарищей:
<code>/1000 рестик > @moj_nik @drug2 @drug3</code>
(после символа '>' перечисляем всех через пробел включая себя)

я оплатил кому-то его покупки:
<code>/300 сувениры > @drug4</code>

я вернул кому-то деньги:
<code>/1300 вернул > @drug5</code>


вбить чужой счет:
<code>/add</code>
далее отвечать на вопросы

удалить неверно вбитый чек
<code>/del</code>
"""


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, help_msg, parse_mode = 'HTML')


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


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
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

class FlaskThread(threading.Thread):
    def run(self) -> None:
        app.run(host="0.0.0.0", port=9086)


# class TelegramThread(threading.Thread):
#     def run(self) -> None:
#         bot.polling(none_stop=True)

if __name__ == "__main__":
    flask_thread = FlaskThread()
    flask_thread.start()

    bot.polling(none_stop=True)