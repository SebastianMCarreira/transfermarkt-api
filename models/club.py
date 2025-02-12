from models.constants import HOST
from bs4 import BeautifulSoup

class Club:
    def __init__(self, name_id: str):
        from models.interface import CachedGet
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
        from models.interface import CachedGet
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
