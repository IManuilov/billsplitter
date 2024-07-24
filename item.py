import json
from datetime import datetime

def nowstr():
    nw = datetime.now()
    date_time = nw.strftime("%d/%m")
    return date_time

class Item:

    def __init__(self, amount, user, description='', date=nowstr(), splitusers=[]):
        self.date = date
        self.amount = amount
        self.user = user
        self.description = description
        self.splitusers = splitusers
        #

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__(),
            sort_keys=True,
            indent=4)

