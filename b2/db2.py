from b2.b2controller import Group
from b2.model import User, Expense

pers_group = Group(-4212554524, 'Поход')
pers_group.users = [
    User(339897034, 'Кеша', '9671487302','Сбер'),
    User(0, 'Маша', '9556547895', 'Тбанк'),
    User(1, 'Лиза', '8672342333', 'Альфа')
]
pers_group.expenses = [
    Expense(0, 200, 'Покупки', 0, [1, 339897034]),
    Expense(1, 300, 'Покупки 2', 0, [0, 1, 339897034]),
    Expense(2, 500, 'Beer', 1, [1, 339897034]),
    Expense(3, 120, 'Bailes', 339897034, [1, 339897034]),
]


def save_group(group: Group):
    global pers_group
    pers_group = group

def load_group_by_id(chatid) -> Group:
    return pers_group

def load_group_by_userid(userid) -> Group:
    return pers_group

# def load_user_by_userid(userid) -> User:
#     pass

# def save_user(user: User):
#     pass

#Group(-4212554524, 'Поход')
#
# grp.users = [
#     User(339897034, 'Кеша', '',''),
#     User(0, 'Маша', '', '')
# ]