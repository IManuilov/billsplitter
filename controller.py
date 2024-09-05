from telebot import types
from telebot.types import ReplyKeyboardMarkup

from cmdparser import trycmd
from item import Item
from database import loadExpenses, saveExpenses
from utils import strmoney


def clear_cmd(message):
    chatid = message.chat.id
    expense = loadExpenses(str(chatid))
    expense.clear()
    saveExpenses(expense)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Я в деле", callback_data='add'))
    return markup

def add_button(call):
    chatid = call.message.chat.id
    username = call.from_user.username

    print('add new user btn', chatid, username)

    expense = loadExpenses(chatid)
    expense.addItem(Item(0, username, ''))
    msg = (f'Добавлен новый участник <code>{username}</code>\n' +
            'Список участников:<code>\n' + '\n'.join(expense.userSet()) + '</code>')
    saveExpenses(expense)
    return msg

def del_button(call):
    n = call.data[3:]
    id = int(n)
    chatid = call.message.chat.id
    expense = loadExpenses(chatid)

    del_it = next((it for it in expense.items if it.id == id), None)

    if del_it:
        expense.items.remove(del_it)
        head = f'Удален расход <code>{del_it.toStr()}</code>'
    else:
        head = 'Расход не найден, возможно уже удален'

    saveExpenses(expense)


    return head + '\n' + get_exp_state(expense)




def get_users(message, ont_time):
    chatid = message.chat.id
    expense = loadExpenses(str(chatid))
    markup = ReplyKeyboardMarkup(row_width=5, resize_keyboard=True, one_time_keyboard=ont_time)

        # markup.add(types.KeyboardButton(text='На всех'))

    for it in expense.userSet():
        markup.add(types.KeyboardButton(text=it))
    if not ont_time:
        markup.add(
            types.KeyboardButton(text='На всех'), types.KeyboardButton(text='Хватит'))

    return markup


def del_cmd(message):
    chatid = message.chat.id
    expense = loadExpenses(str(chatid))
    markup = types.InlineKeyboardMarkup()
    for it in expense.items:
        markup.add(types.InlineKeyboardButton(text=it.toStr(), callback_data='del' + str(it.id)))
    return markup

def add_expense_cmd(message):
    msg = message.text
    user = message.from_user.username
    chatid = message.chat.id
    print(chatid, user, msg)
    cmd = trycmd(msg)
    if not cmd:
        # bot.reply_to(message, 'bad command')
        resp = 'bad command'
    else:

        resp = add_expense(chatid, cmd, user)

    return resp


def add_expense(chatid, cmd, user):
    expense = loadExpenses(str(chatid))
    it = expense.addExp(user, cmd)
    saveExpenses(expense)
    if len(it.splitusers) == 0:
        users = 'все'
    else:
        users = ' '.join(it.splitusers)
    user_count = len(it.splitusers)
    if user_count == 0:
        user_count = len(expense.userSet())
    spl_amount = it.amount / user_count
    head = f'добавлен расход {it.toStr()}.\n{users} должны {user} по {strmoney(spl_amount)} денег'
    resp = head + '\n' + get_exp_state(expense)
    return resp


def get_exp_state(expense):
    t1_all_expenses = expense.printTbl()
    t2_balance = expense.calc()
    resp = ('<pre>'
            + t1_all_expenses
            + '\n\n'
            + t2_balance
            + '</pre>')
    return resp
