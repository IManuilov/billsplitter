from typing import List


class Msg():
    def __init__(self, text, markup, recipient_id):
        self.text = text
        self.markup = markup
        self.recipient_id = recipient_id

class Expense:
    def __init__(self, id: int,  amount: int, name: str, who: int, whom: List[int]):
        self.id = id
        self.amount = amount
        self.name = name
        self.who = who
        self.whom = set(whom)
        self.paid = set()

    def get_debtors(self) -> List[int]:
        return [item for item in self.whom if item not in self.paid] #self.whom - self.paid

    def is_user_in_debtors(self, chatid: int) -> bool:
        for item in self.get_debtors():
            if item == chatid:
                return True
        return False

    def get_for_one_amount(self):
        return self.amount / len(self.whom)

class User:
    def __init__(self, chatid, name, phone, bank):
        self.chatid = chatid
        self.name = name
        self.phone = phone
        self.bank = bank

class Group:
    def __init__(self, chatid, name):
        self.chatid = chatid
        self.name = name
        self.users = []
        self.expenses = []
        self.id_counter = 0

    def get_expense_by_id(self, id):
        for expense in self.expenses:
            if expense.id == id:
                return expense
        return None

    def next_id(self):
        self.id_counter += 1
        return self.id_counter

    def ids_to_users(self, ids):
        return [self.find_user_by_id(id) for id in ids]

    def find_user_by_id(self, userid):
        for usr in self.users:
            if usr.chatid == userid:
                return usr
        return None

    def find_user_by_name(self, username):
        for usr in self.users:
            if usr.name == username:
                return usr
        return None

    def add_user(self, user):
        self.users.append(user)
        return [Msg("You are added", None, user.id)]


    # def add_expense(self, expense):
    #     self.expenses.append(expense)
    #
    #     msgs =[Msg("Ты должен " + expense.who.name + " " + str(expense.amount), None, usr.id)
    #             for usr in expense.whom]
    #     msgs.append(Msg("Расход добавлен", None, expense.who.id))
    #     return msgs

    # def fix_expense(self, who, whom, amount):
    #     expense = Expense(amount, "return", who, whom)
    #     self.expenses.append(expense)

    def show_my_debts(self, user):
        pass

    def settle(self):
        print("settle")
        pass

    def get_user_names(self):
        return [usr.name for usr in self.users]
