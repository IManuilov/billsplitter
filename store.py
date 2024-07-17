import json

import mysql.connector

from Config import config
from cmdparser import trycmd
from groupExpenses import Expenses

print('1')
EXP_TABLE = 'exp3'

DB_USER: 'root'
DB_PASSWORD: 'secret'
DB_HOST: 'localhost'
DB_NAME: 'mySchema'

cnx = mysql.connector.connect(
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    database=config.DB_NAME
    )

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


def loadExpenses(chatid):
    mycursor = cnx.cursor()
    vals = [chatid]
    mycursor.execute(f"SELECT * FROM {EXP_TABLE} where chatid = %s", vals)
    it = mycursor.fetchone()
    if it:
        try:
            print(it[0])
            print(it[1])
            obj = json.loads(it[1])

            obj = Expenses(**obj)
            print(obj.printAll())
            print(obj.calc())
            return obj
        except:
            print('Error reading from DB')
            return Expenses(chatid)
    else:
        return Expenses(chatid)

def saveExpenses(expense):
    mycursor = cnx.cursor()

    data = expense.toJSON()#json.dumps(expense)
    print(data)

    sql = f"REPLACE INTO {EXP_TABLE} (chatid, data) VALUES (%s, %s)"
    val = (expense.chatid, data)
    mycursor.execute(sql, val)

    cnx.commit()

id = '55557'

exp = Expenses(id)
cmd = trycmd('/100 r')
exp.addExp('ilovke', cmd)
saveExpenses(exp)

# exp = loadExpenses(id)
# exp.addItem(Item(300, 'Liza', 'Buhlo2'))
# saveExpenses(exp)

# exp = Expenses('55556')
# exp.addItem(Item('12-11', 100, 'Pool', 'Kesha'))
# saveExpenses(exp.chatid, exp)