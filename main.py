import requests
import os
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
    'Left-Back': 'RBAC',
    'Centre-Back': 'CBAC',
    'Attacking Midfield': 'AMID',
    'Goalkeeper': 'GKEP'
}
CURRENT_CLASS = 'ausfallzeiten_k'

class CachedGet:
    def __init__(self, url: str):
        self.url_path = url.split(HOST)[1]
        self.file_path = url.split(HOST)[1].replace('/',VS)
        if os.path.exists(os.path.join(CACHE_PATH, self.file_path)):
            with open(os.path.join(CACHE_PATH, self.file_path), 'r') as f:
                self.content = f.read()
        else:
            self.content = requests.get(url, headers=HEADERS).content.decode('utf-8')
            print('making request')
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
        self.main_position = bs.find('dd', {'class':'detail-position__position'}).text.strip()
        self.main_position_cat = POSITIONS[bs.find('dd', {'class':'detail-position__position'}).text.strip()]
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
        if 'Former player:' in bs.find('a', {'class':'data-header__box--link'}).text:
            self.player_url = f'https://{HOST}'+bs.find('a', {'class':'data-header__box--link'})['href']
        else:
            self.player_url = None
        self.manager = None
        self.player = None

        self.clubs = [
            {
                'club': club_row.find_all('td')[1].find('a').text,
                'club_url': f'https://{HOST}'+club_row.find_all('td')[1].find('a')['href'],
                'position': club_row.find_all('td')[1].text.replace(club_row.find_all('td')[1].find('a').text,''),
                'appointed': datetime.strptime(club_row.find_all('td')[2].text.split('(')[1], '%b %d, %Y)'),
                'until': 'current' if CURRENT_CLASS in club_row['class'] else datetime.strptime(club_row.find_all('td')[3].text.split('(')[1], '%b %d, %Y)'),
                'matches': 0 if club_row.find_all('td')[4].text.strip() == '-' else int(club_row.find_all('td')[4].text),
                'ppm': float(club_row.find_all('td')[5].text)
            }
            for club_row in bs.find_all('div', {'class':'box'})[3].find_all('tr')[1:] if len(club_row.find_all('td')) > 1
        ]

    def get_player(self):
        if self.player_url:
            self.player = Player(self.player_url)
            return self.player
        else:
            return None
        
    def get_total_ppm(self):
        total_matches = sum([club['matches'] for club in self.clubs])
        cummulative_points = sum([club['matches'] * club['ppm'] for club in self.clubs])
        return cummulative_points / total_matches



# m = Manager('pep-guardiola_5672')
m = Manager('erik-ten-hag_3816')
print('bye')
# CachedGet('https://www.transfermarkt.com/pep-guardiola/profil/spieler/5950')

