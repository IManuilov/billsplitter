import telebot
from telebot.storage import StateMemoryStorage
from telebot import types

from Config import config
from cmdparser import trycmd
from groupExpenses import Expenses, Item
from store import loadExpenses, saveExpenses

#ilovke bot
# TELEBOT_TOKEN = "6964570328:AAEKJbpATcF8etTNegz6kOJCd-zfJFT_C_Q"

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.TELEBOT_TOKEN, state_storage=state_storage)






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
    chatid = message.chat.id
    expense = loadExpenses(str(chatid))
    expense.clear()
    saveExpenses(expense)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Я в деле", callback_data='add'))

    bot.send_message(message.chat.id, 'обнулили', reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id,
                     """
                     \\450 - добавить расход 450, разделить на всех участников 
                     \\450 молоко - добавить расход и комментарий, разделить на всех участников 
                     \\450 молоко -@dima - добавить расход, разделить на всех кроме dima
                     \\450 >@dima @inna - добавить расход, разделить на dima и inna 
                     """)


@bot.message_handler(commands=['del'])
def start_message(message):
    chatid = message.chat.id
    expense = loadExpenses(str(chatid))

    markup = types.InlineKeyboardMarkup()
    for i, it in enumerate(expense.items):
        markup.add(types.InlineKeyboardButton(text=str(it), callback_data='del'+str(i)))

    bot.send_message(message.chat.id, 'удаление', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    if call.data == "add":
        print('add', call)
        chatid = call.message.chat.id
        expense = loadExpenses(chatid)

        expense.addItem(Item(0, call.from_user.username, ''))

        msg = 'Участники:\n' + '\n'.join(expense.userSet())
        bot.send_message(call.message.chat.id, f"<pre>{msg}</pre>", parse_mode = 'HTML')

        saveExpenses(expense)
    elif call.data.startswith("del"):
        n = call.data[3:]
        i = int(n)
        chatid = call.message.chat.id
        expense = loadExpenses(chatid)
        expense.items.remove(expense.items[i])
        saveExpenses(expense)
        table = expense.printAll()
        t2 = expense.calc()
        bot.send_message(call.message.chat.id, '<pre>'+table + '\n' + t2+'</pre>', parse_mode = 'HTML')
    elif call.data.startswith("usr"):
        print(call.data)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    msg = message.text
    user = message.from_user.username
    chatid = message.chat.id
    print(chatid, user, msg)

    cmd = trycmd(msg)
    if not cmd:
        bot.reply_to(message, 'bad command')
        return

    expense = loadExpenses(str(chatid))

    expense.addExp(user, cmd)

    table = expense.printTbl()
    t2 = expense.calc()

    markup = types.InlineKeyboardMarkup()
    # for i, it in enumerate(expense.userSet()):
    #     markup.add(types.InlineKeyboardButton(text=str(it), callback_data='usr' + it))


    resp = ('<pre>'
            + table + '\n\n' + t2
            +'</pre>'
            )
    bot.reply_to(message, resp,
                 parse_mode = 'HTML',
                 reply_markup=markup)

    saveExpenses(expense)




bot.polling(none_stop=True)

