import json

from cmdparser import trycmd
from groupExpenses import Expenses
from store import saveExpenses, loadExpenses

x = {
  "name": "John",
  "age": 30,
  "married": True,
  "divorced": False,
  "children": ("Ann","Billy"),
  "pets": None,
  "cars": [
    {"model": "BMW 230", "mpg": 27.5},
    {"model": "Ford Edge", "mpg": 24.1}
  ]
}

print(json.dumps(x))

def prn(exp):
  print(exp.printTbl())
  print(exp.calc())

id = '12341243234'

for i in range(1,1000):
   e = loadExpenses(id)
   print(i)

# exp = Expenses('123')
# exp.addExp('user1', trycmd('/10 >@user2'))
# prn(exp)
# saveExpenses(exp)
# exp = loadExpenses(id)
#
# exp.addExp('user2', trycmd('/20'))
# exp.addExp('user3', trycmd('/30'))
#
# exp.addExp('user1', trycmd('/20.5 -@user2'))
# exp.addExp('user3', trycmd('/20.4 >@user1'))
#
# print(exp.toJSON())
