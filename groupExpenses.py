import json
from collections import defaultdict



from calc import calc
from item import Item
from table import prep



class Expenses:
    def __init__(self, chatid, items=[], users=[]):
        self.chatid = chatid
        self.items = [Item(**it) for it in items]
        self.users = users


    def addExp(self, user, cmd):
        spl_usr = self.getSplitUsers(cmd)

        self.addItem(Item(cmd['amount'], user, cmd['description'], splitusers=spl_usr))


    def addItem(self, item):
        self.items.append(item)

    def addUser(self, user):
        self.users.append(user)

    def userSet(self):
        return set([it.user for it in self.items])

    def printTbl(self):
        res = defaultdict(list)
        for it in self.items: res[it.date].append(it)

        table = [['money', 'who', 'description', 'excep']]
        for dt, lst in res.items():
            table.append([dt])

            for it in lst:
                table.append([str(it.amount), it.user, it.description, '.'.join(it.splitusers)])

        return prep(table)

    def printAll(self):
        txt = '0123456789012345678901234567890123456789\n'+Item.head()

        res = defaultdict(list)
        for it in self.items: res[it.date].append(it)

        for dt, lst in res.items():
            txt += dt + '\n'
            txt += '\n'.join([str(i) for i in lst])
            txt += '\n'
        return txt

    def calc(self):
        # res = defaultdict(list)
        # for it in self.items: res[it.user].append(it.amount)
        #
        # u2a = {}
        # for u, l in res.items():
        #     u2a[u] = sum(l)
        #
        # if len(u2a) == 0:
        #     return
        #
        # fullsum = sum(u2a.values())
        # expsum = fullsum / len(u2a)
        # table = [['who', 'owed']]   # lent
        # for u, s in u2a.items():
        #     table.append([u, str(s - expsum)])

        u2a = calc(self.items)
        tbl = [['who','balance']]
        for u,a in u2a.items():
            tbl.append([u,str(a)])

        return prep(tbl)

    def clear(self):
        self.items = []

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

    def getSplitUsers(self, cmd):
        spl_usr = []
        if cmd['ultype'] == '>':
            spl_usr = cmd['ulist']
        elif cmd['ultype'] == '-':
            spl_usr = self.userSet() - set(cmd['ulist'])
        return spl_usr

# exp = Expenses()
# exp.addItem(Item('', 100, 'Kesha', 'морковь'))
# exp.addItem(Item('', 200, 'Dima', 'огурцы'))
# exp.addItem(Item('', 50, 'Kesha', 'лук'))
# exp.addItem(Item('', 150, 'Katja', 'вино'))
#
# exp.printAll()
# exp.calc()
