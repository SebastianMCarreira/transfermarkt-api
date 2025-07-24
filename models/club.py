from models.constants import HOST, TRANSFER_FLOWS_QUERY_PARAMS, ACADEMIES_JSON
from models.utils import parse_value, has_academy_suffix
from bs4 import BeautifulSoup

class Club:
    def __init__(self, name_id: str):
        from models.interface import CachedGet
        from models.utils import parse_name_id
        self.name_id = name_id
        self.url_name = name_id.split('_')[0]
        self.id = name_id.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/startseite/verein/{self.id}').content
        bs = BeautifulSoup(self.html, features="html.parser")
        self.name = bs.find('h1').text.strip()
        facts_box = bs.find('div', {'class': 'box daten-und-fakten-verein'})
        self.tel_number = facts_box.find('span', {'itemprop':'telephone'}).text if facts_box.find('span', {'itemprop':'telephone'}) else None
        self.fax_number = facts_box.find('span', {'itemprop':'faxNumber'}).text if facts_box.find('span', {'itemprop':'faxNumber'}) else None
        self.site = facts_box.find('span', {'itemprop':'url'}).text if facts_box.find('span', {'itemprop':'url'}) else None
        related_clubs = bs.find_all('ul', {'class': 'data-header__list-clubs'})[0].find_all('a')
        senior_club_name_id = None
        for related_club in related_clubs:
            rel_club_name_id = parse_name_id(related_club['href'])
            if not has_academy_suffix(rel_club_name_id):
                senior_club_name_id = rel_club_name_id
                break
        self.academy_of = None if senior_club_name_id == self.name_id else Club(senior_club_name_id)
        self.total_value = parse_value(bs.find('a','data-header__market-value-wrapper').text) if bs.find('a','data-header__market-value-wrapper') else 0

    def find_all_academies(self):
        if self.find_parent() is None:
            pass

    def get_staff(self):
        return ClubStaff(self.name_id)
    
    def print_line(self):
        widith = 130
        if self.academy_of:
            left_side = f'{self.name} (academy of {self.academy_of.name})'
        else:
            left_side = f'{self.name}'
        right_side = f'Club(\'{self.name_id}\')'.rjust(widith-len(left_side))
        print(f'{left_side}{right_side}')


class ClubStaff:
    def __init__(self, name_id: str):
        from models.interface import CachedGet
        self.name_id = name_id
        self.url_name = name_id.split('_')[0]
        self.id = name_id.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/mitarbeiter/verein/{self.id}').content
        bs = BeautifulSoup(self.html, features="html.parser")
        self.coaching = [
            {
                'name': coaching_row.find_all('td')[0].text.strip().split('\n')[0].strip(),
                'position': coaching_row.find_all('td')[0].text.strip().split('\n')[-1].strip(),
                'manager_url': f'https://{HOST}'+coaching_row.find_all('td')[0].find('a')['href']
            } for coaching_row in bs.find_all('div', {'class': 'box'})[0].find('tbody').find_all('tr', recursive=False)
        ]
        self.manager = None if len([c for c in self.coaching if c['position'] == 'Manager']) == 0 else [c for c in self.coaching if c['position'] == 'Manager'][0]


class ClubTransferFlows:
    def __init__(self, name_id: str):
        from models.interface import CachedGet
        self.name_id = name_id
        self.url_name = name_id.split('_')[0]
        self.id = name_id.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/transferstroeme/verein/{self.id}/plus/1&{TRANSFER_FLOWS_QUERY_PARAMS}').content
        bs = BeautifulSoup(self.html, features="html.parser")
        self.name = bs.find('h1').text.strip()
        self.image_url = bs.find('div', {'class': 'data-header__profile-container'}).find('img')['src']
        self.total_value = parse_value(bs.find('a','data-header__market-value-wrapper').text) if bs.find('a','data-header__market-value-wrapper') else 0


class ClubSearch:
    def __init__(self, search_str):
        from models.interface import CachedGet
        self.html = CachedGet(f'https://{HOST}/schnellsuche/ergebnis/schnellsuche?query={search_str.replace(' ', '+')}').content
        