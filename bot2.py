from typing import List

import telebot
from telebot import StateMemoryStorage
# from telebot.types import ReplyKeyboardMarkup
from telebot import types
from telebot.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, BotCommand

from Config import config
from b2.model import User, Msg, Expense, Group, Debt
from b2.b2controller import add_user_to_group, add_expense, get_groupid_by_userid, get_group_by_userid, start_group, \
    get_group_by_id, add_payment
from table import prep
from utils import strmoney

state_storage = StateMemoryStorage()
bot = telebot.TeleBot(config.TELEBOT_TOKEN, state_storage=state_storage)

bot.set_my_commands([
    BotCommand(command='/add', description='добавить траты'), # user
    BotCommand(command='/status', description='кому должен'), # user
    BotCommand(command='/pay', description='расчитаться'),    # user
    BotCommand(command='/start', description='начать с нуля'), # grp user
    BotCommand(command='/all', description='показать все траты'), # all
    BotCommand(command='/depts', description='показать только долги'), # all
    # BotCommand(command='/del', description='удаление записей'),
]);

# refactoring -> controller

# save load to BD
# search group by user
# select default group for user if more than one
# disable group commands to user and usercommands to group
# finalization
# delete expense

def send_all(msgs: List[Msg]):
    for msg in msgs:
        print('sendmsg:', msg.recipient_id, msg.text)
        if msg.recipient_id > 1000 or msg.recipient_id < -1000:
            bot.send_message(msg.recipient_id, msg.text, reply_markup=msg.markup)


# add user #
def bank_callback(message, user_data):
    user_data['bank'] = message.text

    user = User(user_data["user_id"], user_data["name"], user_data["phone"], user_data["bank"])

    send_all(add_user_to_group(user, user_data["group_id"]))

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
@bot.message_handler(commands=['start', 'force'])
def start_message(message):
    chat_id = message.chat.id
    print('message.text', message.text, 'chat_id', chat_id)

    if chat_id < 0:
        # для группы
        send_all(start_group(message))
    else:
        # для пользователя
        groupid = message.text.replace("/start ", "")
        if get_group_by_id(groupid) is None:
            bot.send_message(message.chat.id, f'Группа {groupid} не найдена. Надо присоединиться по ссылке из общего чата')
            return

        data = {}
        data['group_id'] = groupid
        data['user_id'] = chat_id

        msg = bot.send_message(message.chat.id, 'Введи свое имя')
        bot.register_next_step_handler(msg, user_name_callback, data)

# add expense

def get_users_markup(all_users, selected_users):
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
            data['debtor_names'] = data['all_users'].copy()
        elif minus:
            data['debtor_names'].remove(usrname)
        elif plus:
            data['debtor_names'].append(usrname)

        markup = get_users_markup(data['all_users'], data['debtor_names'])
        txt = 'На кого делим сумму:\n ' + ' '.join(data['debtor_names']) + '\nДобавить еще'

        msg = bot.send_message(message.chat.id, txt, reply_markup=markup)
        bot.register_next_step_handler(msg, recipients_callback, data)


def expense_name_callback(message, data):
    data['name'] = message.text

    markup = get_users_markup(data['all_users'], data['debtor_names'])
    msg = bot.send_message(message.chat.id, 'На кого делим сумму:', reply_markup=markup)
    bot.register_next_step_handler(msg, recipients_callback, data)


def add_sum_callback(message, data):
    data['amount'] = int(message.text)

    msg = bot.send_message(message.chat.id, 'Наименование:')
    bot.register_next_step_handler(msg, expense_name_callback, data)


@bot.message_handler(commands=['add'])
def add_exp(message):
    chat_id = message.chat.id

    group = get_group_by_userid(chat_id)

    data = {}
    data['creditor_id'] = chat_id
    data['debtor_names'] = []
    data['all_users'] = [usr.name for usr in group.users]
    data['group_id'] = group.chat_id

    msg = bot.send_message(message.chat.id, 'Сумма')
    bot.register_next_step_handler(msg, add_sum_callback, data)


@bot.message_handler(commands=['all'])
def show_group_status_all(message):
    chat_id = message.chat.id
    group = get_group_by_id(chat_id)
    if group is None:
        bot.send_message(message.chat.id, 'Группа не найдена')
        return

    txt = grp_report(group, True)

    bot.send_message(message.chat.id, txt, parse_mode='HTML')

@bot.message_handler(commands=['depts'])
def show_group_status_short(message):
    chat_id = message.chat.id
    group = get_group_by_id(chat_id)
    if group is None:
        bot.send_message(message.chat.id, 'Группа не найдена')
        return

    txt = grp_report(group, False)

    bot.send_message(message.chat.id, txt, parse_mode='HTML')

def grp_report(group: Group, full: bool):
    txt = ''
    for ex in group.expenses:
        txt += f"<B>{group.find_user_by_id(ex.creditor_id).name} заплатил {strmoney(ex.amount)} за '{ex.name}'</B>\n"
        one_amount = strmoney(ex.get_for_one_amount())
        for usr in group.ids_to_users(ex.debtor_ids):
            ok = usr.chat_id in ex.paid_ids or usr.chat_id == ex.creditor_id
            if full or not ok:
                ok_in = '<s>' if ok else ''
                ok_out = '</s>' if ok else ''
                txt += ok_in + one_amount + '\t' + usr.name + ok_out + '\n'
        txt += '\n'

    if len(txt) == 0:
        txt = 'Нет расходов'
    return txt

@bot.message_handler(commands=['status'])
def show_status(message):
    chat_id = message.chat.id
    if chat_id < 0:
        return

    group = get_group_by_userid(chat_id)

    my_creds = group.get_debts(filter_creditor_id=chat_id)

    table = '\n'.join([f"{strmoney(t.amount)} {group.find_user_by_id(t.debtor_id).name} за {t.name}" for t in my_creds])

    txt = f'<B>Тебе должны {strmoney(sum([debt.amount for debt in my_creds]))}</B>\n{table}'
    bot.send_message(message.chat.id, txt, parse_mode='HTML')

    #, parse_mode='MarkdownV2'

    my_debts = group.get_debts(filter_debtor_id=chat_id)

    txt = ""
    for debt in my_debts:
        txt += strmoney(debt.amount) + ' ' + group.find_user_by_id(debt.creditor_id).name + '\n'

    txt = '<B>Ты должен ' + (strmoney(sum([debt.amount for debt in my_debts]))) + '</B>\n' + txt
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

    msgs = add_payment(expense, group, my_id)

    markup = get_buttons_for_pay(group, my_id, expense.creditor_id)
    bot.edit_message_text(callback.message.text,
                          chat_id=callback.message.chat.id,
                          message_id=callback.message.id,
                          reply_markup=markup)

    send_all(msgs)



@bot.callback_query_handler(func=lambda callback: callback.data.startswith('creditor:'))
def select_paid_callback(callback):
    creditor_id = int(callback.data.replace('creditor:', ''))
    my_id = callback.message.chat.id
    group = get_group_by_userid(my_id)
    creditor = group.find_user_by_id(creditor_id)

    my_debts = group.get_debts(filter_creditor_id=creditor_id, filter_debtor_id=my_id)
    sum_amount = sum([d.amount for d in my_debts])

    markup = get_debts_buttons(my_debts)#get_buttons_for_pay(group, my_id, creditor_id)

    txt = f"ты должен {creditor.name} суммарно {sum_amount}\nПеревод по номеру {creditor.phone} в {creditor.bank}\nВыберите расходы которые были оплачены:"

    bot.edit_message_text(txt,
        chat_id=callback.message.chat.id,
        message_id=callback.message.id,
        reply_markup=markup)
    # ,
    #         parse_mode='MarkdownV2'
    # bot.register_next_step_handler(msg, select_exp_callback, data)

def get_debts_buttons(debts: List[Debt]):
    markup = types.InlineKeyboardMarkup()
    for debt in debts:
        markup.add(types.InlineKeyboardButton(str(debt.amount) + " за " + debt.name,
                                                  callback_data='paid:' + str(debt.expid)))

    return markup


def get_buttons_for_pay(group, my_id, usr_to_id):
    markup = types.InlineKeyboardMarkup()
    sum_amount = 0
    for exp in group.expenses:
        if exp.creditor_id == usr_to_id and exp.is_user_in_debtors(my_id):
            sum_amount += exp.get_for_one_amount()
            markup.add(types.InlineKeyboardButton(str(exp.get_for_one_amount()) + " за " + exp.name,
                                                  callback_data='paid:' + str(exp.id)))
    # markup.add(types.InlineKeyboardButton('Все оплачено ' + str(sum_amount), callback_data='all'))
    return markup


@bot.message_handler(commands=['pay'])
def settle(message):
    chat_id = message.chat.id
    group = get_group_by_userid(chat_id)

    my_debts = group.get_debts(filter_debtor_id=chat_id)
    grouped_data = {}
    for debt in my_debts:
        if debt.creditor_id in grouped_data:
            grouped_data[debt.creditor_id] += debt.amount
        else:
            grouped_data[debt.creditor_id] = debt.amount

    markup = types.InlineKeyboardMarkup()
    for chat_id, amount in grouped_data.items():
        usr = group.find_user_by_id(chat_id)
        markup.add(types.InlineKeyboardButton(usr.name + " " + str(amount), callback_data="creditor:"+str(chat_id)))

    bot.send_message(message.chat.id, 'Выбери с кем расчитаться:', reply_markup=markup)


@bot.message_handler(commands=['test'])
def test_data(message):
    group_id = get_group_by_userid(message.chat.id).chat_id

    user = User(3, "Эллурия", "12346789", "somebank")
    send_all(add_user_to_group(user, group_id))

    user = User(4, "Инга", "234678", "somebank2")
    send_all(add_user_to_group(user, group_id))

    user = User(5, "Феофан", "9234678", "somebank3")
    send_all(add_user_to_group(user, group_id))

    exp1 = dict({
        'group_id': group_id,
        'creditor_id': 3,
        'debtor_names': ['Эллурия', 'Инга', 'Феофан', 'Rtif'],
        'amount': 600,
        'name': 'expense1'
    })
    #  sdfsdf
    exp2 = dict({
        'group_id': group_id,
        'creditor_id': 4,
        'debtor_names': ['Феофан', 'Rtif'],
        'amount': 400,
        'name': 'expense2'
    })

    send_all(add_expense(exp1))
    send_all(add_expense(exp2))


# grp = get_group_by_id(-4212554524)
# grp.get_debts()


if __name__ == "__main__":
    print('===============ready===========')

    bot.polling(none_stop=True)


