import json
import sqlite3
import traceback
from typing import Optional

from Config import get_working
from b2.b2controller import Group
from b2.model import User, Expense
from pathlib import Path

# pers_group = Group(-4212554524, 'Поход')
# pers_group.users = [
#     User(339897034, 'Кеша', '9671487302','Сбер'),
#     User(0, 'Маша', '9556547895', 'Тбанк'),
#     User(1, 'Лиза', '8672342333', 'Альфа')
# ]
# pers_group.expenses = [
#     Expense(0, 200, 'Покупки', 0, [1, 339897034]),
#     Expense(1, 300, 'Покупки 2', 0, [0, 1, 339897034]),
#     Expense(2, 500, 'Beer', 1, [1, 339897034]),
#     Expense(3, 120, 'Bailes', 339897034, [1, 339897034]),
# ]


def init():
    global cursor
    global connection
    # Устанавливаем соединение с базой данных
    dbfolder = Path(get_working()) / 'my_database.db'
    print('dbfolder', dbfolder)
    connection = sqlite3.connect(dbfolder, check_same_thread=False)
    cursor = connection.cursor()

    # cursor.execute('''
    #     DROP TABLE groups
    # ''')
    # cursor.execute('''
    #     DROP TABLE user_to_group
    # ''')

    cursor.execute('''
CREATE TABLE IF NOT EXISTS groups (
    chat_id INTEGER PRIMARY KEY,
    data text
)
''')
    cursor.execute('''
CREATE TABLE IF NOT EXISTS user_to_group (
    user_id INTEGER PRIMARY KEY,
    group_id TEXT 
)
''')

def get_cursor():
    global cursor
    return cursor


def save_group(group: Group):
    mycursor = get_cursor()

    data = group.toJSON()

    sql = f"REPLACE INTO groups (chat_id, data) VALUES (?, ?)"
    val = (group.chat_id, data)
    mycursor.execute(sql, val)

    connection.commit()


def load_group_by_id(chat_id) -> Group:
    print('load', chat_id)
    mycursor = get_cursor()
    vals = [chat_id]
    mycursor.execute(f"SELECT * FROM groups where chat_id = ?", vals)
    it = mycursor.fetchone()
    if it:
        try:
            obj = json.loads(it[1])

            print(obj)
            obj = Group(**obj)
            return obj
        except:
            print(traceback.format_exc())
            return None
    else:
        return None

def load_group_by_userid(user_id) -> Optional[Group]:
    group_id = get_group_id_by_user_id(user_id)
    print('load_group_by_userid', group_id)
    if group_id:
        return load_group_by_id(group_id)

    return None


def add_user_id_to_group_mapping(user_id, group_id):
    mycursor = get_cursor()

    sql = f"REPLACE INTO user_to_group (user_id, group_id) VALUES (?, ?)"
    val = (user_id, group_id)
    mycursor.execute(sql, val)

    connection.commit()

def clear_group_mapping(group_id):
    mycursor = get_cursor()

    sql = f"DELETE from user_to_group where group_id = ?"
    param = str(group_id)
    val = (param,)
    print(param, val)
    mycursor.execute(sql, val)

    connection.commit()

def get_group_id_by_user_id(user_id):
    mycursor = get_cursor()
    vals = [user_id]
    mycursor.execute(f"SELECT * FROM user_to_group where user_id = ?", vals)
    it = mycursor.fetchone()
    if it:
        return it[1]

    return None

init()

def prntable(table_name):
    # Execute a query to select all data from the given table
    cursor.execute(f"SELECT * FROM {table_name}")

    # Fetch all results from the executed query
    rows = cursor.fetchall()

    # You can also get the column names from cursor.description
    column_names = [description[0] for description in cursor.description]

    # Print the column names
    print(" | ".join(column_names))

    # Loop through the rows and print them
    for row in rows:
        print(row)

prntable('groups')
prntable('user_to_group')


# # save_group(pers_group)
# grp = load_group_by_id(-4212554524)
# print(grp.expenses)
#
# # add_user_to_group(100,200)
# # add_user_to_group(1,-4212554524)
# print(load_group_by_userid(1))
#
# print(get_group_id_by_user_id(339897034))
#
# grp = load_group_by_userid(339897034)
# for u in grp.users:
#     print(u)
# # print(grp.users)
#
# for e in grp.expenses:
#     print(e)
# # print(grp.expenses)

