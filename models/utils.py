from models.constants import ACADEMY_SUFFIXES

def parse_value(value_str):
    if '?' in value_str:
        return 0
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


def parse_name_id(url):
    if 'http' in url:
        url = url[10:]
    return f'{url.split("/")[1]}_{url.split("/")[4]}'


def is_special_club(text):
    return (
        'Retired' in text or 'Without Club' in text or
        'Unknown' in text or 'Own Youth' in text or
        'Career break' in text
    )


def has_academy_suffix(name):
    if '_' in name:
        name = name.split('_')[0]
    return any([
        name.endswith(suffix) for suffix in ACADEMY_SUFFIXES
    ])
