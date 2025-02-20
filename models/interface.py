import requests, os
from models.constants import HOST, CACHE_PATH, HEADERS, VS, IMAGE_HOST
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

class CachedGetPng:
    def __init__(self, url: str):
        self.url_path = url.split(IMAGE_HOST)[1]
        self.file_path = url.split(IMAGE_HOST)[1].replace('/',VS)
        if os.path.exists(os.path.join(CACHE_PATH, self.file_path)):
            with open(os.path.join(CACHE_PATH, self.file_path), 'rb') as f:
                self.content = f.read()
        else:
            self.content = requests.get(url, headers=HEADERS).content
            print('making request: '+url)   
            with open(os.path.join(CACHE_PATH, self.file_path), 'wb') as f:
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
    
def equal_images(image_a_url, image_b_url):
    image_id_a = image_a_url.split('lm=')[1]
    image_id_b = image_b_url.split('lm=')[1]
    club_id_a = image_a_url.split('/')[-1].split('.png')[0]
    club_id_b = image_b_url.split('/')[-1].split('.png')[0]
    image_a = CachedGetPng(f'https://tmssl.akamaized.net/images/wappen/head/{club_id_a}.png?lm={image_id_a}')
    image_b = CachedGetPng(f'https://tmssl.akamaized.net/images/wappen/head/{club_id_b}.png?lm={image_id_b}')
    return image_a.content == image_b.content
