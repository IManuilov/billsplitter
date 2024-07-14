import telebot
from telebot.storage import StateMemoryStorage

from splitbill.model.groupExpenses import Expenses, Item

#ilovke bot
TELEBOT_TOKEN = "6964570328:AAEKJbpATcF8etTNegz6kOJCd-zfJFT_C_Q"

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(TELEBOT_TOKEN, state_storage=state_storage)

expens = Expenses()


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


@bot.message_handler(commands=['start'])
def start_message(message):
    expens.clear()
    bot.send_message(message.chat.id, 'пусто')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    msg = message.text
    user = message.from_user.username
    chatid = message.chat.id
    print(chatid, user, msg)

    cmd, descr = parse(msg)
    if not cmd:
        return

    expens.addItem(Item('', cmd, user, descr ))

    table = expens.printAll()
    t2 = expens.calc()

    bot.reply_to(message, '<pre>'+table + '\n' + t2+'</pre>', parse_mode = 'HTML')


bot.polling(none_stop=True)

