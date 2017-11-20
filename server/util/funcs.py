def separate_thousands(num):
    return "{:,}".format(num).replace(",", " ")


def starts_conversion(data):
    try:
        cc = data.starts / data.shows
    except ZeroDivisionError:
        cc = 0.0
    return "{:.2f}".format(cc * 100)
