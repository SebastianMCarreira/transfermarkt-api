HOST = 'www.transfermarkt.com'
IMAGE_HOST = 'tmssl.akamaized.net'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36', 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'}
VS = '&$'
CACHE_PATH = './cache/'
POSITIONS = {
    'Central Midfield': 'MIDF',
    'Left Midfield': 'MIDF',
    'Right Midfield': 'MIDF',
    'Defensive Midfield': 'DMID',
    'Centre-Forward': 'FORW',
    'Right Winger': 'WING',
    'Left Winger': 'WING',
    'Right-Back': 'FBAC',
    'Left-Back': 'FBAC',
    'Centre-Back': 'CBAC',
    'Attacking Midfield': 'AMID',
    'Goalkeeper': 'GKEP',
    'Sweeper': 'DMID'
}
CURRENT_CLUB = 'ausfallzeiten_k'
TRANSFER_FLOWS_QUERY_PARAMS = "?saisonIdVon=1893&saisonIdBis=2024&zuab=ab&verein_id="
ACADEMY_SUFFIXES = [
    "II", " B", " C", " D", " E", "Youth",
    "ii",                         "jugend",
    "U23",  "U22", "U21", "U20", "U19", "U18", "U17", "U16", "U15",
    "u23",  "u22", "u21", "u20", "u19", "u18", "u17", "u16", "u15"
    ]
ACADEMIES_JSON = 'academies.json'
