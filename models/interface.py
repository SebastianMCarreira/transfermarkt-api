import requests, os, zstandard, json, io, time
from models.constants import HOST, CACHE_PATH, HEADERS, VS, IMAGE_HOST, API_HOST
from models.player import Player
from models.manager import Manager
from models.league import League
from models.club import Club, ClubStaff

class CachedGet:
    def __init__(self, url: str):
        if HOST in url:
            host = HOST
        elif API_HOST in url:
            host = API_HOST
        else:
            raise ValueError(f"URL must start with {HOST} or {API_HOST}")
        self.url_path = url.split(host)[1]
        self.file_path = url.split(host)[1].replace('/',VS)
        if os.path.exists(os.path.join(CACHE_PATH, self.file_path)):
            with open(os.path.join(CACHE_PATH, self.file_path), 'rb') as f:
                self.content = f.read()
        else:
            success = False
            sleep = 10
            print('making request: '+url)   
            while not success:
                reponse = requests.get(url, headers=HEADERS)
                self.content = reponse.content
                if reponse.status_code == 200:
                    success = True
                else:
                    print(f'[Fetch FAIL] {reponse.status_code} {url}')
                    print(f'Retrying in {sleep} seconds...')
                    time.sleep(sleep)
                    sleep *= 2
            with open(os.path.join(CACHE_PATH, self.file_path), 'wb') as f:
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

def get_json_decompressed(path: str):
    response = CachedGet(f'{API_HOST}/{path}')
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        dctx = zstandard.ZstdDecompressor()
        with dctx.stream_reader(io.BytesIO(response.content)) as reader:
            data = reader.read()
        return json.loads(data)