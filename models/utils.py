def parse_value(value_str):
    value_str = value_str.split()[0]
    value_str = value_str.replace('€','')
    value_str = value_str.replace('$','')
    value_str = value_str.replace('£','')
    if value_str[-2:] == 'bn' or value_str[-2:] == 'Bn':
        multiplier = 1_000_000_000
        value_str = value_str[:-2]
    elif value_str[-1] == 'm' or value_str[-1] == 'M':
        multiplier = 1_000_000
        value_str = value_str[:-1]
    elif value_str[-1] == 'k' or value_str[-1] == 'K':
        multiplier = 1_000
        value_str = value_str[:-1]
    else:
        multiplier = 1
    return float(value_str) * multiplier
