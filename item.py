
from datetime import datetime

def nowstr():
    nw = datetime.now()
    date_time = nw.strftime("%m/%d")
    return date_time

class Item:

    def __init__(self, amount, user, description='', date=nowstr(), splitusers=[]):
        self.date = date
        self.amount = amount
        self.user = user
        self.description = description
        self.splitusers = splitusers
        #

