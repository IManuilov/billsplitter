

def strmoney(fl):
    return ('{0:.2f}'.format(fl)).replace('.00','')

def struser(user, maxlen=None):
    if maxlen:
        user = user[:maxlen]
    return f'<code>{user}</code>'