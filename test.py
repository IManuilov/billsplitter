from cmdparser import trycmd
from groupExpenses import Expenses, Item

exp = Expenses('123')

cmd = trycmd('/0')
exp.addExp('user1', cmd)

cmd = trycmd('/0 r')
exp.addExp('user2', cmd)

cmd = trycmd('/0 r')
exp.addExp('user3', cmd)

cmd = trycmd('/900 sugar ')
exp.addExp('user1', cmd)

print(exp.calc())

cmd = trycmd('/500.12 oil -@user1 ')
exp.addExp('user2', cmd)

cmd = trycmd('/1777.454789 oil -@user1 ')
exp.addExp('user2', cmd)

# print('--')
print(exp.printTbl())
# print('--')

print(exp.calc())