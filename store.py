import json
import traceback

import mysql.connector
from mysql.connector import OperationalError

from Config import config
from cmdparser import trycmd
from groupExpenses import Expenses

print('1')
EXP_TABLE = 'exp3'

DB_USER: 'root'
DB_PASSWORD: 'secret'
DB_HOST: 'localhost'
DB_NAME: 'mySchema'


def connect():
    return mysql.connector.connect(
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        database=config.DB_NAME
    )


cnx = connect()

print('db opened')


CHECK_TABLE = (f"""SELECT * 
    FROM information_schema.tables
    WHERE table_schema = '{config.DB_NAME}' 
        AND table_name = '{EXP_TABLE}'
    LIMIT 1;
""")

DDL = f""" 
CREATE TABLE {EXP_TABLE} (
    chatid varchar(32),
    data text,
	PRIMARY KEY (chatid)
);    
"""

mycursor = cnx.cursor()
mycursor.execute(CHECK_TABLE)
it = mycursor.fetchall()
print(len(it))
if (len(it) == 0):
    mycursor = cnx.cursor()
    mycursor.execute(DDL)


def get_cursor():
    global cnx

    try:
        mycursor = cnx.cursor()
    except (OperationalError) as er:
        print('OperationalError, try reconnect')
        cnx = connect()
        mycursor = cnx.cursor()

    return mycursor

def loadExpenses(chatid):
    print('load', chatid)
    mycursor = get_cursor()
    vals = [chatid]
    mycursor.execute(f"SELECT * FROM {EXP_TABLE} where chatid = %s", vals)
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

    data = expense.toJSON()#json.dumps(expense)
    # print(data)

    sql = f"REPLACE INTO {EXP_TABLE} (chatid, data) VALUES (%s, %s)"
    val = (expense.chatid, data)
    mycursor.execute(sql, val)

    cnx.commit()

