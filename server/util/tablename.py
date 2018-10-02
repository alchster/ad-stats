from transliterate import translit

def tablename(string):
    tn = "".join(filter(str.isalnum,
                        translit(string, 'ru', reverse=True)
                        .encode("ascii", "ignore").decode()))
    if tn == "":
        tn = "__noname"
    if tn[0].isdigit():
        tn = "_%s" % tn
    return tn
