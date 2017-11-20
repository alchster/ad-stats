def tablename(string):
    func = str.isalnum
    if isinstance(string, unicode):
        func = unicode.isalnum
    tn = "".join(filter(func, string.encode("ascii", "ignore")))
    if tn == "":
        tn = "__noname"
    if tn[0].isdigit():
        tn = "_%s" % tn
    return tn
