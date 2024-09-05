from cmdparser import trycmd
from database import saveExpenses, loadExpenses
from groupExpenses import Expenses

# exp = Expenses('123')
exp = loadExpenses('123')
exp.addExp('user2', trycmd('/20 >@user2'))

saveExpenses(exp)

e2 = loadExpenses('123')


print(e2.printTbl())