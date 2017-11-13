def tablename(string):
    tn = "".join(filter(str.isalnum, string))
    if tn[0].isdigit():
        tn = "_%s" % tn
    return tn
