import telebot
from telebot.storage import StateMemoryStorage
from telebot import types
from telebot.types import ReplyKeyboardRemove

from Config import config
from cmdparser import get_cmd
from controller import add_button, del_button, add_expense_cmd, del_cmd, clear_cmd, get_users, add_expense
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

# @bot.inline_handler(func=lambda query: len(query.query) > 0)
# def query_text(query):
#     print('query', query)
#     prompt = types.InlineQueryResultArticle(id=1, title='user1', description='polz1',
#                                             input_message_content=types.InputTextMessageContent(
#                                                 message_text="kesha"
#                                             ))
#     bot.answer_inline_query(query.id, [prompt])

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

    # bot.send_message(message.chat.id, horoscope_message, parse_mode="Markdown")

# команда для запуска визарда для добавления расхода
@bot.message_handler(commands=['add'])
def start_message(message):
    markup = get_users(message, True)

    msg = bot.send_message(message.chat.id, 'Выберите, кто заплатил?', reply_markup=markup)
    # объект для хранения ввода пользователя на всех шагах
    data = {}
    bot.register_next_step_handler(msg, who_callback, data)

# adding expense script
@bot.message_handler(commands=['del'])
def start_message(message):
    markup = del_cmd(message)

    bot.send_message(message.chat.id, 'удаление', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "add":
        msg = add_button(call)

        bot.send_message(call.message.chat.id, msg, parse_mode='HTML')

    elif call.data.startswith("del"):
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
                 parse_mode = 'HTML',
                 reply_markup=markup)






bot.polling(none_stop=True)

