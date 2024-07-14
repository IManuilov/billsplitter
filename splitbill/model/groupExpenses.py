from collections import defaultdict


class Item:
    def __init__(self, date, amount, user, description):
        self.date = date
        self.amount = amount
        self.user = user
        self.description = description
        #

    def __str__(self):
        return f"{self.amount:9} | {self.user[:7]:7} | {self.description[:10]:10} | {self.date:5}"

class Expenses:
    def __init__(self):
        self.chatid = ''
        self.items = []
        self.users = []


    def addItem(self, item):
        self.items.append(item)

    def addUser(self, user):
        self.users.append(user)

    def printAll(self):
        table = (self.chatid + " Все расходы :\n" +
                 '\n'.join([str(it) for it in self.items]))
        print(table)
        return table
    def calc(self):
        res = defaultdict(list)
        for it in self.items: res[it.user].append(it.amount)

        u2a = {}
        for u, l in res.items():
            u2a[u] = sum(l)


        fullsum = sum(u2a.values())
        expsum = fullsum / len(u2a)
        table = ('Кто     |   Сколько\n' +
            ''.join([f"{u} | {s-expsum}\n"  for u, s in u2a.items()]))

        print(table)
        return  table

    def clear(self):
        self.items = []

# exp = Expenses()
# exp.addItem(Item('', 100, 'Kesha', 'морковь'))
# exp.addItem(Item('', 200, 'Dima', 'огурцы'))
# exp.addItem(Item('', 50, 'Kesha', 'лук'))
# exp.addItem(Item('', 150, 'Katja', 'вино'))
#
# exp.printAll()
# exp.calc()
