def get_option_value(options, option_name, default_value):
    return options[option_name] if option_name in options else default_value
