import logging

def tablename(string):
    logging.debug("Transforming '%s' to table name", string)
    tn = "".join(filter(str.isalnum, string.encode("ascii", "ignore")))
    if tn == "":
        tn = "__noname"
    if tn[0].isdigit():
        tn = "_%s" % tn
    return tn
