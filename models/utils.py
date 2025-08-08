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


def tm_minute_span_to_str(minute_span):
    _, x, y = minute_span['style'].replace(';','').split(' ') # Split background-position coords
    extra = '' if '\n    \xa0' == minute_span.text else minute_span.text.strip() # Get extra minutes if exist ('+2' for example)
    x = int(x.replace('-','').replace('px', '')) # Convert coords to ints
    y = int(y.replace('-','').replace('px', ''))
    # Minute images are spaced in 36x26px with 10 minute images per row starting from minute 1
    # and 12 rows up to the minute 120
    units = (x/36)+1 if x < 324 else 0
    tens = y/36
    minute = int(units + tens * 10) # Calculate minute from units and tens
    return f"{minute}{extra}"
