from telebot.types import ReplyKeyboardRemove

from b2.model import Group, User, Expense, Msg
from b2.db2 import save_group, load_group_by_userid, load_group_by_id


def start_group(message):
    print("start_group")
    group = Group(message.chat.id, message.chat.title)
    save_group(group)
    return group

def add_user_to_group(user, groupid):
    print("add_user_to_group")

    group = load_group_by_id(groupid)
    group.users.append(user)
    save_group(group)

    return [
        Msg(f"Ты добавлен в группу {group.name}", None, user.chatid),
        Msg(f"{user.name} добавлен.\n {", ".join(group.get_user_names())}", None, group.chatid)
    ]


def get_users_for_userid(userid):
    group = load_group_by_userid(userid)
    return [usr.name for usr in group.users]

def return_expense(return_data):
    pass


def get_group_by_id(groupid) -> Group:
    group = load_group_by_id(groupid)
    return group

def get_group_by_userid(userid) -> Group:
    group = load_group_by_userid(userid)
    return group


def get_groupid_by_userid(userid) -> int:
    group = load_group_by_userid(userid)
    return group.chatid

def add_expense(exp_data):
    print(exp_data)
    # exp_data["whom"]  exp_data["user_names"]
    group = load_group_by_id(exp_data["groupid"])
    user_paid = group.find_user_by_id(exp_data["who"])

    users = [group.find_user_by_name(usrname) for usrname in exp_data["whom"]]
    whomids = [usr.chatid for usr in users if usr is not None]
    if len(whomids) == 0:
        return [
            Msg("Нет пользователей для этого расхода", None, exp_data["who"])
        ]

    expense = Expense(group.next_id(), exp_data["amount"], exp_data["name"], exp_data["who"], whomids)
    group.expenses.append(expense)

    save_group(group)

    users_except_you = ", ".join([usr.name for usr in users if usr != user_paid])

    for_one_amount = expense.get_for_one_amount()
    lsfmsg = Msg(f"Расход добавлен. {users_except_you} должны тебе по {for_one_amount}", ReplyKeyboardRemove(), exp_data["who"])

    other_msg = f"{user_paid.name} заплатил за {expense.name}. Ты должен ему {for_one_amount} "

    msgs = [Msg(other_msg, None, usrid) for usrid in whomids]
    # todo: кнопка "Вернул"

    msgs.append(lsfmsg)

    return msgs


def show_my_debts(userid):

    return [Msg("", None, userid)]

