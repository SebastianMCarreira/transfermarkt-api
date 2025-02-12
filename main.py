import requests
import os
import csv
from datetime import datetime
from bs4 import BeautifulSoup

HOST = 'www.transfermarkt.com'
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

def get_object(url: str):
    parts = url.split('/')
    if '/profil/spieler/' in url:
        return Player(f'{parts[3]}_{parts[6]}')
    elif '/profil/trainer/' in url:
        return Manager(f'{parts[3]}_{parts[6]}')
    elif '/startseite/wettbewerb/' in url:
        return League(f'{parts[3]}_{parts[6]}')
    elif '/startseite/verein/' in url:
        return Club(f'{parts[3]}_{parts[6]}')
    elif '/mitarbeiter/verein/' in url:
        return ClubStaff(f'{parts[3]}_{parts[6]}')

class CachedGet:
    def __init__(self, url: str):
        self.url_path = url.split(HOST)[1]
        self.file_path = url.split(HOST)[1].replace('/',VS)
        if os.path.exists(os.path.join(CACHE_PATH, self.file_path)):
            with open(os.path.join(CACHE_PATH, self.file_path), 'r') as f:
                self.content = f.read()
        else:
            self.content = requests.get(url, headers=HEADERS).content.decode('utf-8')
            print('making request: '+url)
            with open(os.path.join(CACHE_PATH, self.file_path), 'w') as f:
                f.write(self.content)

class Player:
    def __init__(self, name_id: str):
        self.name_id = name_id
        self.url_name = name_id.split('_')[0]
        self.id = name_id.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/profil/spieler/{self.id}').content
        bs = BeautifulSoup(self.html)
        self.name = bs.find('h1').text.strip()
        self.main_position = None if bs.find('dd', {'class':'detail-position__position'}) == None else bs.find('dd', {'class':'detail-position__position'}).text.strip()
        self.main_position_cat = None if not self.main_position else POSITIONS[self.main_position]
        if bs.find('a', {'class':'data-header__box--link'}).find('span',{'class':'data-header__content'}).text.strip() == 'Manager':
            self.manager_url = f'https://{HOST}'+bs.find('a', {'class':'data-header__box--link'})['href']
        else:
            self.manager_url = None
        self.manager = None

    def get_manager(self):
        if self.manager_url:
            self.manager = Manager(self.manager_url)
            return self.manager
        else:
            return None
        

class Manager:
    def __init__(self, name_id: str):
        self.name_id = name_id
        self.url_name = name_id.split('_')[0]
        self.id = name_id.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/profil/trainer/{self.id}').content
        bs = BeautifulSoup(self.html)
        self.name = bs.find('h1').text.strip()
        if bs.find('a', {'class':'data-header__box--link'}) and 'Former player:' in bs.find('a', {'class':'data-header__box--link'}).text:
            self.player_url = f'https://{HOST}'+bs.find('a', {'class':'data-header__box--link'})['href']
        else:
            self.player_url = None
        self.manager = None
        self.player = None
        clubs_box = [b for b in bs.find_all('div', {'class':'box'}) if b.find('h2') and 'History' in b.find('h2').text][0]
        self.clubs = [
            {
                'club': club_row.find_all('td')[1].find('a').text,
                'club_url': f'https://{HOST}'+club_row.find_all('td')[1].find('a')['href'],
                'position': club_row.find_all('td')[1].text.replace(club_row.find_all('td')[1].find('a').text,''),
                'appointed': datetime.strptime(club_row.find_all('td')[2].text.split('(')[1], '%b %d, %Y)') if '(' in club_row.find_all('td')[2].text else None,
                'until': 'current' if CURRENT_CLUB in club_row['class'] else datetime.strptime(club_row.find_all('td')[3].text.split('(')[1], '%b %d, %Y)') if '(' in club_row.find_all('td')[3].text else None,
                'matches': 0 if club_row.find_all('td')[4].text.strip() == '-' else int(club_row.find_all('td')[4].text),
                'ppm': float(club_row.find_all('td')[5].text)
            }
            for club_row in clubs_box.find_all('tr')[1:] if len(club_row.find_all('td')) > 1
        ]
        current = None if len([c for c in self.clubs if c['until'] == 'current']) == 0 else [c for c in self.clubs if c['until'] == 'current'][0]
        self.current_club_name = current['club'] if current else None
        self.current_club_url = current['club_url'] if current else None

    def get_player(self):
        if self.player_url:
            self.player = get_object(self.player_url)
            return self.player
        else:
            return None
        
    def get_total_ppm(self):
        total_matches = self.get_total_matches()
        cummulative_points = sum([club['matches'] * club['ppm'] for club in self.clubs])
        return cummulative_points / total_matches
    
    def get_total_matches(self):
        return sum([club['matches'] for club in self.clubs])
    
    def get_clubs(self):
        return [get_object(club['club_url']) for club in self.clubs]

class League:
    def __init__(self, name_code: str):
        self.name_id = name_code
        self.url_name = name_code.split('_')[0]
        self.code = name_code.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/startseite/wettbewerb/{self.code}').content
        bs = BeautifulSoup(self.html)
        self.name = bs.find('h1').text.strip()
        self.current_clubs = [
            {
                'club': club_row.find_all('td')[1].text.strip(),
                'club_url': f'https://{HOST}'+club_row.find_all('td')[1].find('a')['href'],
            } for club_row in bs.find_all('table')[1].find_all('tr')[2:]
        ]

    def get_clubs(self):
        return [get_object(club['club_url']) for club in self.current_clubs]
    

class Club:
    def __init__(self, name_id: str):
        self.name_id = name_id
        self.url_name = name_id.split('_')[0]
        self.id = name_id.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/startseite/verein/{self.id}').content
        bs = BeautifulSoup(self.html)
        self.name = bs.find('h1').text.strip()
    
    def get_staff(self):
        return ClubStaff(self.name_id)
    
class ClubStaff:
    def __init__(self, name_id: str):
        self.name_id = name_id
        self.url_name = name_id.split('_')[0]
        self.id = name_id.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/mitarbeiter/verein/{self.id}').content
        bs = BeautifulSoup(self.html)
        self.coaching = [
            {
                'name': coaching_row.find_all('td')[0].text.strip().split('\n')[0].strip(),
                'position': coaching_row.find_all('td')[0].text.strip().split('\n')[-1].strip(),
                'manager_url': f'https://{HOST}'+coaching_row.find_all('td')[0].find('a')['href']
            } for coaching_row in bs.find_all('div', {'class': 'box'})[0].find('tbody').find_all('tr', recursive=False)
        ]
        self.manager = None if len([c for c in self.coaching if c['position'] == 'Manager']) == 0 else [c for c in self.coaching if c['position'] == 'Manager'][0]


# m = Manager('pep-guardiola_5672')
# m = Manager('andoni-iraola_60677')
leagues = [
    'premier-league_GB1',
    'laliga_ES1',
    'ligue-1_FR1',
    'bundesliga_L1',
    'serie-a_IT1',
    'torneo-inicia_ARG1',
    'campeonato-brasileiro-serie-a_BRA1',
    'major-league-soccer_MLS1',
    'saudovskaa-pro-liga_SA1',
    'liga-nos_PO1',
    'eredivisie_NL1',
    'super-lig_TR1',
    'jupiler-pro-league_BE1',
    'super-league-1_GR1'
]


table = []
for l in leagues:
    league = League(l)
    for c in league.current_clubs:
        club = get_object(c['club_url'])
        manager = get_object(club.get_staff().manager['manager_url']) if club.get_staff().manager else None
        table.append({
            'league': league.name,
            'club': club.name,
            'manager': manager.name if manager else None,
            'position': (manager.player.main_position_cat if manager.get_player() else None) if manager else None,
            'ppm': manager.get_total_ppm() if manager else None,
            'matches': manager.get_total_matches() if manager else None
        })

print(table)
with open('output.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, table[0].keys())
    writer.writeheader()
    writer.writerows(table)
