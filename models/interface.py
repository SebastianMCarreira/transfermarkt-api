import requests, os
from models.constants import HOST, CACHE_PATH, HEADERS, VS
from models.player import Player
from models.manager import Manager
from models.league import League
from models.club import Club, ClubStaff

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
