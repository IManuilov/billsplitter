import json
from collections import defaultdict

from datetime import datetime


def nowstr():
    nw = datetime.now()
    date_time = nw.strftime("%m/%d")
    return date_time

class Item:

    def __init__(self, amount, user, description, date=nowstr()):
        self.date = date
        self.amount = amount
        self.user = user
        self.description = description
        #

    def __str__(self):
        return f"{self.amount:9} | {self.user[:7]:7} | {self.description[:10]:11} | {self.date:5}"

    @staticmethod
    def head():
        return f"{'amount':9} | {'user':7} | {'description':11} | {'date':5}\n"

class Expenses:
    def __init__(self, chatid, items=[], users=[]):
        self.chatid = chatid
        self.items = [Item(**it) for it in items]
        self.users = users


    def addItem(self, item):
        self.items.append(item)

    def addUser(self, user):
        self.users.append(user)

    def userSet(self):
        return set([it.user for it in self.items])

    def printAll(self):
        table = (Item.head() +
                 '\n'.join([str(it) for it in self.items]))
        print(table)
        return table
    def calc(self):
        res = defaultdict(list)
        for it in self.items: res[it.user].append(it.amount)

        u2a = {}
        for u, l in res.items():
            u2a[u] = sum(l)

        if len(u2a) == 0:
            return

        fullsum = sum(u2a.values())
        expsum = fullsum / len(u2a)
        table = ('Кто     |   Сколько\n' +
            ''.join([f"{u} | {s-expsum}\n"  for u, s in u2a.items()]))

        print(table)
        return  table

    def clear(self):
        self.items = []

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

# exp = Expenses()
# exp.addItem(Item('', 100, 'Kesha', 'морковь'))
# exp.addItem(Item('', 200, 'Dima', 'огурцы'))
# exp.addItem(Item('', 50, 'Kesha', 'лук'))
# exp.addItem(Item('', 150, 'Katja', 'вино'))
#
# exp.printAll()
# exp.calc()
