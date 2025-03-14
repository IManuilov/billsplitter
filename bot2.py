from typing import List

import telebot
from telebot import StateMemoryStorage
# from telebot.types import ReplyKeyboardMarkup
from telebot import types
from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, BotCommand

from Config import config
from b2.model import User, Msg, Expense
from b2.b2controller import add_user_to_group, add_expense, get_groupid_by_userid, get_group_by_userid, start_group
from table import prep
from utils import strmoney

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.TELEBOT_TOKEN, state_storage=state_storage)

bot.set_my_commands([
    BotCommand(command='/add', description='добавить траты'),
    BotCommand(command='/status', description='кому должен'),
    BotCommand(command='/settle', description='расчитаться'),
    BotCommand(command='/start', description='начать с нуля'),
    # BotCommand(command='/del', description='удаление записей'),
]);

def send_all(msgs: List[Msg]):
    for msg in msgs:
        print('sendmsg:', msg.recipient_id, msg.text)
        if msg.recipient_id > 1000:
            bot.send_message(msg.recipient_id, msg.text, reply_markup=msg.markup)


# add user #
def bank_callback(message, user_data):
    user_data['bank'] = message.text

    user = User(user_data["userid"], user_data["name"], user_data["phone"], user_data["bank"])

    send_all(add_user_to_group(user, user_data["groupid"]))

# add user #
def phone_callback(message, data):
    data['phone'] = message.text
    msg = bot.send_message(message.chat.id, 'Введи свой банк для перевода денег')
    bot.register_next_step_handler(msg, bank_callback, data)

# add user #
def user_name_callback(message, data):
    data['name'] = message.text
    msg = bot.send_message(message.chat.id, 'Введи свой номер для перевода денег')
    bot.register_next_step_handler(msg, phone_callback, data)


# start in group
@bot.message_handler(commands=['start'])
def start_message(message):
    chatid = message.chat.id
    print(message)
    print('message.text', message.text, 'chatid', chatid)

    state_storage.data["grp"] = chatid
    # markup = clear_cmd(message)
    if chatid < 0:
        group = start_group(message)

        bot.send_message(group.chatid, 'Новая группа. добавляйся https://t.me/ilovke_bot?start=' + str(chatid))
        #, reply_markup=markup)
    else:
        # спросить имя телефон банк
        msg = bot.send_message(message.chat.id, 'Введи свое имя')

        data = {}
        data['groupid'] = message.text.replace("/start ", "")
        data['userid'] = chatid
        bot.register_next_step_handler(msg, user_name_callback, data)

# add expense

def get_users_markup(all_users, selected_users):
    # expense = loadExpenses(str(chatid))
    markup = ReplyKeyboardMarkup(row_width=5, resize_keyboard=True)

    for it in all_users:
        added = it in selected_users
        markup.add(types.KeyboardButton(text=it + ('-' if added else '+')))

    markup.add(
        types.KeyboardButton(text='На всех'),
        types.KeyboardButton(text='Ок'))

    return markup

def recipients_callback(message, data):
    print('recipients_callback', message.text)


    if message.text == 'Ок':
        send_all(add_expense(data))
        print(data)

    else:
        plus = message.text.endswith('+')
        minus = message.text.endswith('-')
        usrname = message.text.replace('+', '').replace('-', '')

        if message.text == 'На всех':
            data['whom'] = data['all_users'].copy()
        elif minus:
            data['whom'].remove(usrname)
        elif plus:
            data['whom'].append(usrname)

        markup = get_users_markup(data['all_users'], data['whom'])
        txt = 'На кого делим сумму:\n ' + ' '.join(data['whom']) + '\nДобавить еще'

        msg = bot.send_message(message.chat.id, txt, reply_markup=markup)
        bot.register_next_step_handler(msg, recipients_callback, data)


def expense_name_callback(message, data):
    data['name'] = message.text

    markup = get_users_markup(data['all_users'], data['whom'])
    msg = bot.send_message(message.chat.id, 'На кого делим сумму:', reply_markup=markup)
    bot.register_next_step_handler(msg, recipients_callback, data)


def add_sum_callback(message, data):
    print('add sum', message.text)
    data['amount'] = int(message.text)

    msg = bot.send_message(message.chat.id, 'Наименование:')
    bot.register_next_step_handler(msg, expense_name_callback, data)


@bot.message_handler(commands=['add'])
def add_exp(message):
    chatid = message.chat.id

    group = get_group_by_userid(chatid)

    msg = bot.send_message(message.chat.id, 'Сумма')
    data = {}
    data['who'] = chatid
    data['whom'] = []
    data['all_users'] = [usr.name for usr in group.users]
    data['groupid'] = group.chatid
    bot.register_next_step_handler(msg, add_sum_callback, data)


@bot.message_handler(commands=['status'])
def show_status(message):
    chatid = message.chat.id
    group = get_group_by_userid(chatid)

    tomeex = [ex for ex in group.expenses if ex.who == chatid]

    tome = []
    for ex in tomeex:
        for usr in group.ids_to_users(ex.whom):
            if usr.chatid != chatid:
                tome.append((ex.get_for_one_amount(), ex.name, usr.name))

    txt = 'Тебе должны\n'+'\n'.join([str(t) for t in tome])
    bot.send_message(message.chat.id, txt)
    #, parse_mode='MarkdownV2'


    ioweex = [ex for ex in group.expenses if chatid in ex.get_debtors()]
    iowe = []
    for ex in ioweex:
        if ex.who != chatid:
            iowe.append((strmoney(ex.get_for_one_amount()), ex.name, group.ids_to_users([ex.who])[0].name))

    tb = "<pre>" + prep(iowe) + "</pre>"
    txt = 'Ты должен\n' + tb #'\n'.join([str(t) for t in iowe])
    bot.send_message(message.chat.id, txt, parse_mode='HTML')#, parse_mode='MarkdownV2'


def select_exp_callback(message, data):
    print(message.text)

    msg = bot.send_message(message.chat.id, 'Долг', reply_markup=ReplyKeyboardRemove())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('paid:'))
def paid_callback(callback):
    my_id = callback.message.chat.id
    group = get_group_by_userid(my_id)

    exp_id = int(callback.data.replace('paid:', ''))

    expense = group.get_expense_by_id(exp_id)
    expense.paid.add(my_id)

    me = group.find_user_by_id(my_id)
    he = group.find_user_by_id(expense.who)
    amount = str(expense.get_for_one_amount())

    send_all([
        Msg(f'возврат {he.name} {amount} за {expense.name}', None, my_id),
        Msg(f'{me.name} вернул {amount} за {expense.name}', None, expense.who)
        ])


@bot.callback_query_handler(func=lambda callback: True)
def select_paid_callback(callback):
    # print('select_paid_callback', callback)
    print('select_paid_callback', callback.data)
    usr_to_id = int(callback.data)

    my_id = callback.message.chat.id
    group = get_group_by_userid(my_id)
    usr_to = group.find_user_by_id(usr_to_id)


    markup = types.InlineKeyboardMarkup()

    sum_amount = 0
    for exp in group.expenses:
        if exp.who == usr_to_id and exp.is_user_in_debtors(my_id):
            sum_amount += exp.get_for_one_amount()
            markup.add(types.InlineKeyboardButton(str(exp.get_for_one_amount()) + " за " + exp.name,
                                                  callback_data='paid:' + str(exp.id)))

    markup.add(types.InlineKeyboardButton('Все оплачено ' + str(sum_amount), callback_data='all'))

    txt = f"Перевод {usr_to.name} по номеру *`{usr_to.phone}`* в {usr_to.bank}\nВыберите расходы которые были оплачены"


    msg = bot.send_message(callback.message.chat.id, txt + ' Что погасить?',
                           reply_markup=markup,
                           parse_mode='MarkdownV2')

    # bot.register_next_step_handler(msg, select_exp_callback, data)


@bot.message_handler(commands=['settle'])
def settle(message):
    chatid = message.chat.id
    group = get_group_by_userid(chatid)

    iowe_expens = [ex for ex in group.expenses if chatid in ex.get_debtors()]
    iowe = []
    for ex in iowe_expens:
        if ex.who != chatid:
            iowe.append((ex.get_for_one_amount(), ex.who))

    grouped_data = {}
    for item in iowe:
        amount, chatid = item
        if chatid in grouped_data:
            grouped_data[chatid] += amount
        else:
            grouped_data[chatid] = amount

    markup = types.InlineKeyboardMarkup()
    for chatid, amount in grouped_data.items():
        usr = group.find_user_by_id(chatid)
        markup.add(types.InlineKeyboardButton(usr.name + " " + str(amount), callback_data=str(chatid)))

    bot.send_message(message.chat.id, 'Выбери с кем расчитаться:', reply_markup=markup)
    # bot.register_next_step_handler(msg, select_paid_callback, data)


print('ready')
if __name__ == "__main__":
    bot.polling(none_stop=True)


