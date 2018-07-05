def separate_thousands(num):
    return "{:,}".format(num).replace(",", " ")


def starts_conversion(data):
    try:
        cc = data.shows / data.starts
    except ZeroDivisionError:
        cc = 0.0
    return "{:.2f}".format(cc * 100)
