from models.constants import HOST, TRANSFER_FLOWS_QUERY_PARAMS, ACADEMIES_JSON
from models.utils import parse_value
from bs4 import BeautifulSoup

class Club:
    def __init__(self, name_id: str):
        from models.interface import CachedGet
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
        self.academy_of = None
        self.total_value = parse_value(bs.find('a','data-header__market-value-wrapper').text) if bs.find('a','data-header__market-value-wrapper') else 0

    def find_parent(self):
        if self.academy_of is None:
            academy_of = ClubTransferFlows(self.name_id).find_senior_team(avoid=[])
            self.academy_of = Club(academy_of) if academy_of else None
        return self.academy_of
    
    def find_all_academies(self):
        if self.find_parent() is None:
            pass


    def get_staff(self):
        return ClubStaff(self.name_id)
    
    def print_line(self):
        widith = 120
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

    def find_senior_team(self, avoid = []):
        import json
        with open(ACADEMIES_JSON, 'r') as f:
            known_academies = json.load(f)
            if self.name_id in known_academies:
                if 'academy_of' in known_academies[self.name_id]:
                    return known_academies[self.name_id]['academy_of']
                elif 'academies' in known_academies[self.name_id]:
                    return None
        avoid.append(self.id)
        bs = BeautifulSoup(self.html, features="html.parser")
        transfer_flow_rows = bs.find('table', {'class': 'items'}).find_all('tr')[1:]
        for row in transfer_flow_rows:
            url_name = row.find_all('td')[2].find('a')['href'].split('/')[1]
            id = row.find_all('td')[2].find('a')['href'].split('/')[4]
            if id in avoid:
                continue
            name_id = f'{url_name}_{id}'
            # print(f'name_id: {name_id}\tavoid: {avoid}')
            image_url = row.find_all('td')[1].find('img')['src']
            if check_club_similarity(self.name_id, self.image_url, name_id, image_url):
                possible_parent = ClubTransferFlows(name_id)
                if possible_parent.total_value < self.total_value:
                    continue
                parents_parent = possible_parent.find_senior_team(avoid=avoid)
                if parents_parent is None:
                    with open(ACADEMIES_JSON, 'r') as f:
                        known_academies = json.load(f)
                    with open(ACADEMIES_JSON, 'w') as f:
                        known_academies[self.name_id] = {'academy_of': possible_parent.name_id}
                        if possible_parent.name_id in known_academies:
                            known_academies[possible_parent.name_id]['academies'].append(self.name_id)
                        else:
                            known_academies[possible_parent.name_id] = {'academies': [self.name_id]}
                        json.dump(known_academies, f)
                    return possible_parent.name_id
                else:
                    with open(ACADEMIES_JSON, 'r') as f:
                        known_academies = json.load(f)
                    with open(ACADEMIES_JSON, 'w') as f:
                        known_academies[self.name_id] = {'academy_of': parents_parent}
                        if parents_parent in known_academies:
                            known_academies[parents_parent]['academies'].append(self.name_id)
                        else:
                            known_academies[parents_parent] = {'academies': [self.name_id]}
                        json.dump(known_academies, f)
                    return parents_parent
        with open(ACADEMIES_JSON, 'r') as f:
            known_academies = json.load(f)
        with open(ACADEMIES_JSON, 'w') as f:
            known_academies[self.name_id] = {'academies': []}
            json.dump(known_academies, f)
        return None

def check_club_similarity(club_a_name_id, club_a_image_url, club_b_name_id, club_b_image_url):
    from models.interface import equal_images
    if club_a_image_url.split('lm=')[1] == club_b_image_url.split('lm=')[1]:
        return True
    elif abs(int(club_a_image_url.split('lm=')[1]) - int(club_b_image_url.split('lm=')[1])) < 5:
        if equal_images(club_a_image_url, club_b_image_url):
            return True
    club_a = Club(club_a_name_id)
    club_b = Club(club_b_name_id)
    if club_a.fax_number and club_a.fax_number == club_b.fax_number:
        return True
    if club_a.tel_number and club_a.tel_number == club_b.tel_number:
        return True
    if club_a.site and club_a.site == club_b.site:
        return True
    return False


class ClubSearch:
    def __init__(self, search_str):
        from models.interface import CachedGet
        self.html = CachedGet(f'https://{HOST}/schnellsuche/ergebnis/schnellsuche?query={search_str.replace(' ', '+')}').content
        