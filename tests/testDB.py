from cmdparser import trycmd
from database import saveExpenses, loadExpenses
from groupExpenses import Expenses
from item import Item

chatid = "54547"
# expense = loadExpenses(chatid)
# expense.users.append("username1")
# saveExpenses(expense)
#
# expense = loadExpenses(chatid)
# expense.users.append("username2")
# saveExpenses(expense)
#
# expense = loadExpenses(chatid)
# expense.users.append("username3")
# saveExpenses(expense)

expense = loadExpenses(chatid)


print(expense.users)

# expense.addItem(Item(10, "username2", '', splitusers=['username2', 'username3']))
# saveExpenses(expense)

print(expense.printTbl(), expense.calc())