def tablename(string):
    tn = "".join(filter(str.isalnum,
                        string.encode("ascii", "ignore").decode()))
    if tn == "":
        tn = "__noname"
    if tn[0].isdigit():
        tn = "_%s" % tn
    return tn
