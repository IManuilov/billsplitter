import telebot
from telebot.storage import StateMemoryStorage
from telebot import types

from groupExpenses import Expenses, Item
from store import loadExpenses, saveExpenses

#ilovke bot
TELEBOT_TOKEN = "6964570328:AAEKJbpATcF8etTNegz6kOJCd-zfJFT_C_Q"

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(TELEBOT_TOKEN, state_storage=state_storage)

def parse(msg):
    msg = msg.replace('/', '')

    spl = msg.split(' ', 1)

    if spl[0].isdigit():
        descr = ''
        if len(spl) > 1:
            descr = spl[1]

        return int(spl[0]), descr

    else:
        return None, None


# embedded db scripts
# db best practice
# конфиг
# help
# показывать список команд при /
# удаление кнопки
# взаиморасчеты
# + регистрация юзеров

@bot.message_handler(commands=['start'])
def start_message(message):
    chatid = message.chat.id
    expense = loadExpenses(str(chatid))
    expense.clear()
    saveExpenses(expense)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Я в деле", callback_data='add'))

    bot.send_message(message.chat.id, 'обнулили', reply_markup=markup)


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


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    msg = message.text
    user = message.from_user.username
    chatid = message.chat.id
    print(chatid, user, msg)

    cmd, descr = parse(msg)
    if not cmd:
        return

    expense = loadExpenses(str(chatid))
    expense.addItem(Item(cmd, user, descr))

    table = expense.printAll()
    t2 = expense.calc()

    bot.reply_to(message, '<pre>'+table + '\n' + t2+'</pre>', parse_mode = 'HTML')

    saveExpenses(expense)

bot.polling(none_stop=True)

