from bs4 import BeautifulSoup
from models.constants import HOST, POSITIONS

class Player:
    def __init__(self, name_id: str):
        from models.interface import get_json_decompressed
        from datetime import datetime
        self.name_id = name_id
        self.url_name = name_id.split('_')[0]
        self.id = name_id.split('_')[1]
        json_data = get_json_decompressed(f'players?ids[]={self.id}')
        self.name = json_data['data'][0]['name']
        self.short_name = json_data['data'][0]['shortName']
        self.date_of_birth = datetime.strptime(json_data['data'][0]['lifeDates']['dateOfBirth'], "%Y-%m-%d").date()
        self.place_of_birth = json_data['data'][0]['birthPlaceDetails']['placeOfBirth']
        self.country_of_birth_id = json_data['data'][0]['birthPlaceDetails']['countryOfBirthId']
        self.nationality_id = json_data['data'][0]['nationalityDetails']['nationalities']['nationalityId']
        self.main_position = json_data['data'][0]['attributes']['position']['shortName']
        self.main_position_cat = json_data['data'][0]['attributes']['position']['category']

    def get_manager(self):
        from models.interface import get_object
        if self.manager_url:
            self.manager = get_object(self.manager_url)
            return self.manager
        else:
            return None
        
    def get_all_matches(self):
        from models.interface import get_json_decompressed
        json_data = get_json_decompressed(f'/player/{self.id}/performance-game')
        self.all_matches_ids = json_data['data']['gameIds']
        return self.all_matches_ids

    def __repr__(self):
        return f'Player(name={self.name}, id={self.id}, main_position={self.main_position}, main_position_cat={self.main_position_cat})'

class PlayerTransfer:
    def __init__(self, transfer_row):
        pass

