from bs4 import BeautifulSoup
from models.constants import HOST, CURRENT_CLUB
from datetime import datetime

class Manager:
    def __init__(self, name_id: str):
        from models.interface import CachedGet
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
        from models.interface import get_object
        if self.player_url:
            self.player = get_object(self.player_url)
            return self.player
        else:
            return None
        
    def get_total_ppm(self):
        total_matches = self.get_total_matches()
        cummulative_points = sum([club['matches'] * club['ppm'] for club in self.clubs])
        return cummulative_points / total_matches if total_matches else None
    
    def get_total_matches(self):
        return sum([club['matches'] for club in self.clubs])
    
    def get_clubs(self):
        from models.interface import get_object
        return [get_object(club['club_url']) for club in self.clubs]

class AvailableManagers:
    def __init__(self):
        from models.interface import CachedGet
        self.html = CachedGet(f'https://{HOST}/trainer/verfuegbaretrainer/statistik').content
        bs = BeautifulSoup(self.html)
        self.managers = [
            {
                'manager': manager_row.find_all('td')[0].text.strip().split('\n')[0].strip(),
                'manager_url': f'https://{HOST}'+manager_row.find_all('td')[0].find('a')['href']
            }
            for manager_row in bs.find('div', {'class': 'responsive-table'}).find('tbody').find_all('tr', recursive=False)[1:]
        ]
