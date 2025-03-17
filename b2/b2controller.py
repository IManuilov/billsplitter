from telebot.types import ReplyKeyboardRemove

from b2.model import Group, User, Expense, Msg
from b2.db2 import save_group, load_group_by_userid, load_group_by_id, add_user_id_to_group_mapping, clear_group_mapping


def start_group(message):
    chat_id = message.chat.id
    group = get_group_by_id(chat_id)
    if group is not None and len(group.get_debts()) > 0 and not message.text.startswith('/force'):
        return [Msg(group.chat_id,
     'Группа уже существует. Что бы пересоздать выполните команду /force. Все предыдущие траты будут удалены')]

    group = start_group_int(message)

    return [Msg(group.chat_id,
                     'Создана новая группа. Добавляйся по ссылке https://t.me/ilovke_bot?start=' + str(chat_id))]


def start_group_int(message):
    print("start_group")
    group = Group(message.chat.id, message.chat.title)
    save_group(group)
    clear_group_mapping(group.chat_id)


    return group

def add_user_to_group(user, group_id):
    print("add_user_to_group")

    group = load_group_by_id(group_id)
    group.users.append(user)
    save_group(group)
    add_user_id_to_group_mapping(user.chat_id, group_id)

    return [
        Msg(user.chat_id, f"Ты добавлен в группу {group.name}"),
        Msg(group.chat_id, f"{user.name} добавлен. Участники:\n {"\n".join(group.get_user_names())}")
    ]


def get_users_for_userid(userid):
    group = load_group_by_userid(userid)
    return [usr.name for usr in group.users]

def return_expense(return_data):
    pass


def get_group_by_id(groupid) -> Group:
    if groupid < 0:
        group = load_group_by_id(groupid)
    else:
        group = get_group_by_userid(groupid)

    return group

def get_group_by_userid(userid) -> Group:
    group = load_group_by_userid(userid)
    return group


def get_groupid_by_userid(userid) -> int:
    group = load_group_by_userid(userid)
    return group.chat_id

def add_expense(exp_data):
    print("add_expense", exp_data)
    group = load_group_by_id(exp_data["group_id"])
    creditor = group.find_user_by_id(exp_data["creditor_id"])

    debtors = [group.find_user_by_name(usr_name) for usr_name in exp_data["debtor_names"]]
    debtors_ids = [usr.chat_id for usr in debtors if usr is not None]

    if len(debtors_ids) == 0:
        return [
            Msg(exp_data["creditor_id"], "Нет пользователей для этого расхода")
        ]

    expense = Expense(group.next_id(), exp_data["amount"], exp_data["name"], exp_data["creditor_id"], debtors_ids)
    group.expenses.append(expense)

    save_group(group)

    users_except_you = ", ".join([usr.name for usr in debtors if usr != creditor])

    for_one_amount = expense.get_for_one_amount()
    lsfmsg = Msg(exp_data["creditor_id"],
                 f"Расход добавлен. {users_except_you} должны тебе по {for_one_amount}",
                 ReplyKeyboardRemove())

    other_msg = f"{creditor.name} заплатил за {expense.name}. Ты должен ему {for_one_amount} "

    msgs = [Msg(usrid, other_msg) for usrid in debtors_ids]
    # todo: кнопка "Вернул"

    msgs.append(lsfmsg)

    return msgs


def add_payment(expense, group, my_id):

    expense.paid_ids.add(my_id)

    debtor = group.find_user_by_id(my_id)
    creditor = group.find_user_by_id(expense.creditor_id)
    amount = str(expense.get_for_one_amount())
    # save_group(group)

    save_group(group)

    msgs = [
        # себе
        Msg(my_id, f'возврат {creditor.name} {amount} за {expense.name}'),
        # кому вернул
        Msg(expense.creditor_id, f'{debtor.name} вернул {amount} за {expense.name}')
    ]

    return msgs

