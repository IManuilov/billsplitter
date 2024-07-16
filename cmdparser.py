


def trycmd(str):
    if not str.startswith('/'):
        print('error')
        return None
    str = str[1:]

    spl = str.split(' ', 1)

    amount_str = spl[0]
    amount = retr_amount(amount_str)
    if amount == None:
        return None

    next_str = spl[1] if len(spl) > 0 else ''
    descr, ultype, ulist = retreive(next_str)

    return {
        'amount': amount,
        'description': descr,
        'ultype': ultype,
        'ulist': ulist
    }


def retr_amount(str):
    try:
        return float(str)
    except:
        return None


def retreive(str):

    ultype = '-' if '-' in str else ('>' if '>' in str else '')
    if ultype == '':
        return str, '', []

    spl = str.split(ultype)
    ul = [u.replace('@', '').strip() for u in spl[1].split(' ') if u]

    return spl[0].strip(), ultype, ul

# print(retreive('молоко'))
# print(retreive('молоко -'))
#
# print(retreive('молоко -@ilovke'))
# print(retreive('молоко -@ilovke @liza'))
# print(retreive('молоко  -@ilovke  @liza '))
# print(retreive(' молоко   > @ilovke   @liza  '))
# print(retreive(' молоко>@ilovke @liza'))
#
# print(trycmd('/1000 пиво и водка >@ilovke @liza'))
# print(trycmd('/1000  пиво  и водка   >  @ilovke    @liza  '))
# print(trycmd('/100.53 пиво >@ilovke @liza'))
# print(trycmd('/100.53 пиво'))
# print(trycmd('/100.53  '))
#
# print(trycmd('/100,54 пиво >@ilovke @liza'))
#
# print(trycmd('/r1000  пиво  и водка   >  @ilovke    @liza  '))