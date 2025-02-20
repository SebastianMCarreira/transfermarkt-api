from bs4 import BeautifulSoup
from models.constants import HOST

class League:
    def __init__(self, name_code: str):
        from models.interface import CachedGet
        self.name_id = name_code
        self.url_name = name_code.split('_')[0]
        self.code = name_code.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/startseite/wettbewerb/{self.code}').content
        bs = BeautifulSoup(self.html, features="html.parser")
        self.name = bs.find('h1').text.strip()
        self.current_clubs = [
            {
                'club': club_row.find_all('td')[1].text.strip(),
                'club_url': f'https://{HOST}'+club_row.find_all('td')[1].find('a')['href'],
            } for club_row in bs.find_all('table')[1].find_all('tr')[2:]
        ]

    def get_clubs(self):
        from models.interface import get_object
        return [get_object(club['club_url']) for club in self.current_clubs]
