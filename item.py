import json
from datetime import datetime

from utils import strmoney


def nowstr():
    nw = datetime.now()
    date_time = nw.strftime("%d/%m")
    return date_time

class Item:
    def get_id(self):
        return self.id

    def __init__(self, amount, user, description='', date=nowstr(), splitusers=[], id=None):
        self.id = id
        self.date = date
        self.amount = amount
        self.user = user
        self.description = description
        self.splitusers = splitusers
        #

    def toStr(self):
        return f"{strmoney(self.amount)} {self.user} {self.description}"

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__(),
            sort_keys=True,
            indent=4)

