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

def tm_formation_position_to_position(formation_div):
    if formation_div['style'] in ['top: 80%; left: 40%;']:
        return 'GK'
    elif formation_div['style'] in ['top: 63%; left: 28%;']:
        return 'CBL'
    elif formation_div['style'] in ['top: 63%; left: 52.5%;']:
        return 'CBD'
    elif formation_div['style'] in ['']:
        return 'CBC'
    elif formation_div['style'] in ['top: 61%; left: 7.5%;']:
        return 'LB'
    elif formation_div['style'] in ['']:
        return 'LWB'
    elif formation_div['style'] in ['top: 61%; left: 73%;']:
        return 'RB'
    elif formation_div['style'] in ['']:
        return 'RWB'
    elif formation_div['style'] in ['top: 39%; left: 40%;', 'top: 43%; left: 28%;']:
        return 'DM'
    elif formation_div['style'] in ['top: 43%; left: 52%;']:
        return 'DM2'
    elif formation_div['style'] in ['top: 28%; left: 27%;']:
        return 'MC'
    elif formation_div['style'] in ['top: 28%; left: 53%;']:
        return 'MC2'
    elif formation_div['style'] in ['top: 23%; left: 40%;']:
        return 'AM'
    elif formation_div['style'] in ['']:
        return 'AM2'
    elif formation_div['style'] in ['']:
        return 'LMF'
    elif formation_div['style'] in ['']:
        return 'RMF'
    elif formation_div['style'] in ['top: 3%; left: 40%;']:
        return 'CF'
    elif formation_div['style'] in ['']:
        return 'SS'
    elif formation_div['style'] in ['top: 10%; left: 15%;', 'top: 18%; left: 15%;']:
        return 'LW'
    elif formation_div['style'] in ['top: 10%; left: 65%;', 'top: 18%; left: 65%;']:
        return 'RW'
    else:
        raise ValueError(f"Unknown position coordinates: {formation_div['style']}")

def player_anchor_to_name_id(player_anchor):
    return player_anchor['href'][1:].replace('/profil/spieler/','_')
