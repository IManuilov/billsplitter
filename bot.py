import telebot
from telebot.storage import StateMemoryStorage
from telebot import types

from Config import config
from controller import add_button, del_button, add_expense_cmd, del_cmd, clear_cmd
from store import loadExpenses, saveExpenses


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


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     """примеры запросов:
<code>/450</code> добавить расход 450, разделить на всех участников 
<code>/450 билеты</code> - добавить расход и комментарий, разделить на всех участников 
<code>/450 магазин -@dima</code> - добавить расход, разделить на всех участников кроме dima
<code>/450 гостиница >@dima @inna</code> - добавить расход, разделить между dima и inna 
<code>/del</code> выбрать для удаления
<code></code>
""", parse_mode = 'HTML')


# команда для вывода кнопок удаления расходов
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

