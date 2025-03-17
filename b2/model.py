import json
from typing import List, Optional


class Msg:
    def __init__(self, recipient_id, text, markup=None):
        self.recipient_id = recipient_id
        self.text = text
        self.markup = markup

class Debt:
    def __init__(self, creditor_id: int, debtor_id: int, amount: int, expid: int, name: str):
        self.creditor_id = creditor_id
        self.debtor_id = debtor_id
        self.amount = amount
        self.expid = expid
        self.name = name


class Expense:
    def __init__(self, id: int, amount: int, name: str, creditor_id: int, debtor_ids: List[int], paid_ids=[]):
        self.id = id
        self.amount = amount
        self.name = name
        self.creditor_id = creditor_id
        self.debtor_ids = set(debtor_ids)
        print("paid_ids", paid_ids)
        self.paid_ids = set(paid_ids)

    def __str__(self):
        return f"exp: {self.id} {self.amount} {self.name} {self.creditor_id} {self.debtor_ids} {self.paid_ids}"

    def get_debtors(self) -> List[int]:
        return [item for item in self.debtor_ids if item not in self.paid_ids and item != self.creditor_id]

    def is_user_in_debtors(self, chat_id: int) -> bool:
        for item in self.get_debtors():
            if item == chat_id:
                return True
        return False

    def get_for_one_amount(self):
        return self.amount / len(self.debtor_ids)

class User:
    def __init__(self, chat_id, name, phone, bank):
        self.chat_id = chat_id
        self.name = name
        self.phone = phone
        self.bank = bank

    def __str__(self):
        return f"{self.chat_id} {self.name} {self.phone} {self.bank}"


def serial(o):
    if isinstance(o, set):
        return [i for i in o]
    return o.__dict__

class Group:
    def __init__(self, chat_id, name, users=[], expenses=[], id_counter=0):
        self.chat_id = chat_id
        self.name = name
        self.users = [User(**it) for it in users]
        self.expenses = [Expense(**it) for it in expenses]
        self.id_counter = id_counter

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: serial(o),
            sort_keys=True,
            indent=4)

    def get_debts(self, filter_creditor_id: Optional[int]=None, filter_debtor_id: Optional[int]=None) -> List[Debt]:
        result = []
        for exp in self.expenses:
            for debtor_id in exp.get_debtors():
                if ((filter_creditor_id is None or exp.creditor_id == filter_creditor_id)
                        and (filter_debtor_id is None or filter_debtor_id == debtor_id)):
                    result.append(Debt(exp.creditor_id, debtor_id, exp.get_for_one_amount(), exp.id, exp.name))

        return result

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
            if usr.chat_id == userid:
                return usr
        return 'None ' + str(userid)

    def find_user_by_name(self, username):
        for usr in self.users:
            if usr.name == username:
                return usr
        return None

    def add_user(self, user):
        self.users.append(user)
        return [Msg(user.id, "You are added")]


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
