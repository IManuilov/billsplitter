


def prep(table):

    maxwidth = []
    truncwidth = []

    for row in table:
        for i, cell in enumerate(row):
            if len(maxwidth) <= i:
                maxwidth.append(0)
            maxwidth[i] = max(maxwidth[i], len(cell))

    # print(maxwidth)
    truncwidth = maxwidth.copy()
    ptr = 1
    while sum(truncwidth) > 35 - len(maxwidth):
        im = truncwidth.index(max(truncwidth[1:]),1)
        # print(im)
        truncwidth[im] -= 1
    # print(truncwidth)
    # print('------')
    txt = ''
    for r in table:
        if len(r) == 1:
            dst = r[0]
        else:
            dst = ''
            for i,c in enumerate(r):
                mx = truncwidth[i]
                val = c[:mx]
                val = val.rjust(mx)
                if len(dst) > 0:
                    dst = dst + '|'
                dst = dst + val
        txt = txt + '\n' + dst

    # print(txt)
    return txt

# tbl =  [['1','user123', 'hflskd6666jhlkjsfhg','except'],
#         ['16/7'],
#         ['10000', 'q', 'gg'],
#         ['100000', '4', '323423','']]
# prep(tbl)