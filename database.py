import sqlite3
import json
import traceback

from pathlib import Path

from Config import config, get_working
from groupExpenses import Expenses


def init():
    global cursor
    global connection
    # Устанавливаем соединение с базой данных
    dbfolder = Path(get_working()) / 'my_database.db'
    print('dbfolder', dbfolder)
    connection = sqlite3.connect(dbfolder, check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute('''
CREATE TABLE IF NOT EXISTS exp3 (
    chatid TEXT PRIMARY KEY,
    data text
)
''')

def get_cursor():
    global cursor
    return cursor

def loadExpenses(chatid):
    print('load', chatid)
    mycursor = get_cursor()
    vals = [chatid]
    mycursor.execute(f"SELECT * FROM exp3 where chatid = ?", vals)
    it = mycursor.fetchone()
    if it:
        try:
            obj = json.loads(it[1])

            obj = Expenses(**obj)
            return obj
        except:
            print(traceback.format_exc())
            return Expenses(chatid)
    else:
        return Expenses(chatid)

def saveExpenses(expense):
    mycursor = get_cursor()

    data = expense.toJSON()

    sql = f"REPLACE INTO exp3 (chatid, data) VALUES (?, ?)"
    val = (expense.chatid, data)
    mycursor.execute(sql, val)

    connection.commit()



# def save_doc(id, user, file):
#     today = datetime.today()
#     formatted_date = today.strftime("%Y.%m.%d %H:%M:%S")
#
#     cursor.execute('INSERT INTO upload (id, user, file, date) VALUES (?, ?, ?, ?)',
#                    (id, user, file, formatted_date))
#     connection.commit()
#
#
# def vote_doc(id, vote):
#     cursor.execute('UPDATE upload set vote = ? where id = ?',
#                    (vote, id))
#     connection.commit()
#
# def find_all():
#     cursor.execute('select * from upload')
#     users = cursor.fetchall()
#     return users
#
# def to_obj(users):
#     print('findall:')
#     lst = []
#     for us in users:
#         upl = {
#             'id': us[0],
#             'user': us[1],
#             'file': us[2],
#             'date': us[3],
#             'vote': us[4]
#         }
#         lst.append(upl)
#         print(upl)
#     return lst
#
# def save_category(upload_id, category):
#     cursor.execute('INSERT INTO category_vote (upload_id, category_name) VALUES (?, ?)',
#                    (upload_id, category))
#     id = cursor.lastrowid
#
#     connection.commit()
#     return id
#
# def vote_category(id, vote):
#     cursor.execute('UPDATE category_vote set vote = ? where id = ?',
#                    (vote, int(id)))
#     connection.commit()
#
# def find_all_category():
#     cursor.execute('''
# select up.id, up.user, up.file, up.date, up.vote, cv.category_name, cv.vote
# from category_vote cv
# inner join upload up on up.id = cv.upload_id
#     ''')
#     users = cursor.fetchall()
#     return users


init()



