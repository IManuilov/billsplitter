import json

import mysql.connector

from groupExpenses import Expenses, Item

print('1')
cnx = mysql.connector.connect(user='root',
                              password='secret',
                              host='localhost',
                              database='mySchema'
                              )

print('2')

def loadExpenses(chatid):
    mycursor = cnx.cursor()
    vals = [chatid]
    mycursor.execute("SELECT * FROM exp2 where chatid = %s", vals)
    it = mycursor.fetchone()
    if it:
        print(it[0])
        print(it[1])
        obj = json.loads(it[1])

        obj = Expenses(**obj)
        print(obj.printAll())
        print(obj.calc())
        return obj
    else:
        return Expenses(chatid)

def saveExpenses(expense):
    mycursor = cnx.cursor()

    data = expense.toJSON()#json.dumps(expense)
    print(data)

    sql = "REPLACE INTO exp2 (chatid, data) VALUES (%s, %s)"
    val = (expense.chatid, data)
    mycursor.execute(sql, val)

    cnx.commit()

id = '55557'

# exp = Expenses(id)
# exp.addItem(Item('12-11', 100, 'Kesha', 'Cake'))
# saveExpenses(exp)

exp = loadExpenses(id)
exp.addItem(Item('11-11', 300, 'Liza', 'Buhlo2'))
saveExpenses(exp)

# exp = Expenses('55556')
# exp.addItem(Item('12-11', 100, 'Pool', 'Kesha'))
# saveExpenses(exp.chatid, exp)