from item import Item


def calc(items):
    allusers = set([it.user for it in items]);
    for it in items:
        for su in it.splitusers:
            allusers.add(su)

    user2am = {us:0 for us in allusers}

    for it in items:

        split = allusers if len(it.splitusers) == 0 else it.splitusers
        lend = it.amount / len(split)
        user2am[it.user] -= it.amount
        for us in split:
            user2am[us] += lend

    # for u,a in user2am.items():
    #     print(u, a)

    return user2am

# ilv dim liz kat
# calc([
#     Item(0, 'dim'),
#     Item(0, 'liz'),
#     Item(200, 'kat', splitusers=['kat', 'dim']),
#     Item(400, 'ilv'),
#     Item(100, 'liz', splitusers=['ilv']),
#     Item(200, 'dim', splitusers=['ilv'])
# ])
