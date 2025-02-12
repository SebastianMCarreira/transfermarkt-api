from bs4 import BeautifulSoup
from models.constants import HOST, POSITIONS

class Player:
    def __init__(self, name_id: str):
        from models.interface import CachedGet
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
        from models.interface import get_object
        if self.manager_url:
            self.manager = get_object(self.manager_url)
            return self.manager
        else:
            return None
