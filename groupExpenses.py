import json
from collections import defaultdict



from calc import calc
from item import Item
from table import prep
from utils import strmoney


def serial(o):
    # print(o)
    if isinstance(o, set):
        return [i for i in o]
    return o.__dict__


class Expenses:
    def __init__(self, chatid, items=[], users=[]):
        self.chatid = chatid
        self.items = [Item(**it) for it in items]
        self.users = users

        if not all(it.id != None for it in self.items):
            for i, it in enumerate(self.items):
                it.id = i

    def get_last_id(self):
        it = max(self.items, key=lambda i : i.get_id(), default=None)
        if it:
            return it.id
        else:
            return 0

    def addExp(self, user, cmd):
        spl_usr = self.getSplitUsers(cmd)
        last_id = self.get_last_id()
        it = Item(cmd['amount'], user, cmd['description'], splitusers=spl_usr, id=last_id + 1)
        self.addItem(it)
        return it


    def addItem(self, item):
        self.items.append(item)

    def addUser(self, user):
        self.users.append(user)

    def userSet(self):
        return set(self.users)

        # allusers = set([it.user for it in self.items]);
        # for it in self.items:
        #     for su in it.splitusers:
        #         allusers.add(su)
        # return allusers

    def printTbl(self):
        res = defaultdict(list)
        for it in self.items: res[it.date].append(it)

        table = [['сумма', 'кто', 'описание', 'кому']]
        for dt, lst in res.items():
            table.append([dt])

            for it in lst:
                amount_s = strmoney(it.amount)
                table.append([amount_s, it.user, it.description, '.'.join(it.splitusers)])

        return prep(table)


    def calc(self):

        u2a = calc(self.items, self.users)
        tbl = [['who','balance']]
        for u,a in u2a.items():
            tbl.append([u,strmoney(a)])

        return prep(tbl)

    def clear(self):
        self.items = []
        self.users = []

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: serial(o),
            sort_keys=True,
            indent=4)

    def getSplitUsers(self, cmd):
        spl_usr = []
        if cmd['ultype'] == '>':
            spl_usr = cmd['ulist']
        elif cmd['ultype'] == '-':
            spl_usr = set(self.users) - set(cmd['ulist'])
        return spl_usr

# exp = Expenses()
# exp.addItem(Item('', 100, 'Kesha', 'морковь'))
# exp.addItem(Item('', 200, 'Dima', 'огурцы'))
# exp.addItem(Item('', 50, 'Kesha', 'лук'))
# exp.addItem(Item('', 150, 'Katja', 'вино'))
#
# exp.printAll()
# exp.calc()
