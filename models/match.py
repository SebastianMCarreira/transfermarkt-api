from bs4 import BeautifulSoup
from models.constants import HOST
from models.utils import tm_minute_span_to_str, tm_formation_position_to_position, player_anchor_to_name_id
from functools import total_ordering

class Match:
    def __init__(self, match_id:str):
        from models.interface import CachedGet
        self.id = match_id
        self.html = CachedGet(f'{HOST}/spielbericht/index/spielbericht/{self.id}').content
        bs = BeautifulSoup(self.html, features="html.parser")
        self.match_events = []
        for section in bs.find_all('div', {'class': 'large-12 columns'}):
            if 'Referee' in section.text: # Match data section
                continue
            elif 'This match' in section.text: # Ghost? section
                continue
            elif 'Timeline' in section.text: # Timeline section
                continue
            elif 'Line-Ups' in section.find('h2').text.strip(): # Line-ups section
                self.home_club = MatchClub(section.find_all('div', {'class': 'large-6'})[0])
                self.away_club = MatchClub(section.find_all('div', {'class': 'large-6'})[1])
            elif 'Goals' in section.find('h2').text.strip(): # Goals section
                self.match_events.extend([Goal(event_row) for event_row in section.find_all('div', {'class': 'sb-aktion'})])
            elif 'Substitutions' in section.find('h2').text.strip(): # Substitutions section
                self.match_events.extend([Substitution(event_row) for event_row in section.find_all('div', {'class': 'sb-aktion'})])
            elif 'Cards' in section.find('h2').text.strip(): # Bookings section
                self.match_events.extend([Booking(event_row) for event_row in section.find_all('div', {'class': 'sb-aktion'})])
            elif 'Penalty shoot-out' in section.find('h2').text.strip(): # Shoot-out section
                continue
            elif 'Special events' in section.find('h2').text.strip(): # Special events section
                continue
            else:
                raise ValueError(f"Unknown section: {section.find('h2').text.strip()}")
        self.match_events.sort()

@total_ordering
class MatchEvent:
    def __init__(self, event_row):
        minute_span = event_row.find('span')
        self.minute_str = tm_minute_span_to_str(minute_span)
        self.minute_int = int(self.minute_str.split('+')[0]) if '+' in self.minute_str else int(self.minute_str)
        self.minute_int_ext = int(self.minute_str.split('+')[1]) if '+' in self.minute_str else 0
        if self.minute_int < 46:
            self.half = 0
        elif self.minute_int < 91:
            self.half = 1
        elif self.minute_int < 106:
            self.half = 2
        elif self.minute_int < 121:
            self.half = 3
        main_player_name_id = player_anchor_to_name_id(event_row.find_all('div', {'class': 'sb-aktion-spielerbild'})[0].find('a'))
        self.main_player = main_player_name_id

    def __str__(self):
        return f"{self.minute_str}: {self.main_player}"
    
    def _is_valid_operand(self, other):
        return (hasattr(other, "minute_int") and
                hasattr(other, "minute_int_ext"))
    
    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        if self.minute_int < other.minute_int:
            return True
        elif self.minute_int == other.minute_int:
            return self.minute_int_ext < other.minute_int_ext
        else:
            return False
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.minute_int == other.minute_int and self.minute_int_ext == other.minute_int_ext

class Goal(MatchEvent):
    def __init__(self, event_row):
        super().__init__(event_row)
        self.goalscorer_name_id = self.main_player
        assistant_url = event_row.find('div', {'class': 'sb-aktion-aktion'}).find_all('a')[1]['href'] if len(event_row.find('div', {'class': 'sb-aktion-aktion'}).find_all('a')) == 2 else None
        self.assistant_name_id = assistant_url[1:].split('/saison')[0].replace('/leistungsdatendetails/spieler/', '_') if assistant_url else None
        goal_details_lines = event_row.find('div', {'class': 'sb-aktion-aktion'}).text.split('\n')
        self.goal_type = goal_details_lines[1].split(',')[1].strip() if len(goal_details_lines[1].split(',')) == 3 else None
        self.assist_type = goal_details_lines[2].split(',')[1].strip() if self.assistant_name_id and len(goal_details_lines[2].split(',')) == 3 else None
        self.scoreboard = event_row.find_all('div', {'class': 'sb-aktion-spielstand'})[0].text.strip()

    def __str__(self):
        goal_str = f"{self.goalscorer_name_id} ({self.goal_type})" if self.goal_type else self.goalscorer_name_id
        assist_str = f" Assist: {self.assistant_name_id} ({self.assist_type})" if self.assist_type else f" Assist: {self.assistant_name_id}" if self. assistant_name_id else ''
        return f"{self.minute_str}: Goal: {goal_str}{assist_str} [{self.scoreboard}]"

class Substitution(MatchEvent):
    def __init__(self, event_row):
        super().__init__(event_row)
        self.subbed_out_name_id = self.main_player
        self.subbed_in_name_id = player_anchor_to_name_id(event_row.find('div', {'class': 'sb-aktion-aktion'}).find('div', {'class': {'sb-aktion-spielerbild'}}).find('a'))
        self.sub_type = event_row.find('div', {'class': 'sb-aktion-spielstand hide-for-small'}).find('span')['title'] if event_row.find('div', {'class': 'sb-aktion-spielstand hide-for-small'}) else None
    
    def __str__(self):
        if self.sub_type:
            return f"{self.minute_str}: Out: {self.subbed_out_name_id} In: {self.subbed_in_name_id} [{self.sub_type}]"
        else:
            return f"{self.minute_str}: Out: {self.subbed_out_name_id} In: {self.subbed_in_name_id}"

class Booking(MatchEvent):
    def __init__(self, event_row):
        super().__init__(event_row)
        self.booked_player = self.main_player
        self.reason = event_row.find('div', {'class': 'sb-aktion-aktion'}).text.split('\n')[1].strip().split(',')[1].strip() if len(event_row.find('div', {'class': 'sb-aktion-aktion'}).text.split('\n')[1].strip().split(',')) == 2 else None
        if 'sb-gelb' in event_row.find('div', {'class': 'sb-aktion-spielstand'}).find('span')['class']:
            self.card = 'Yellow' 
        elif 'sb-rot' in event_row.find('div', {'class': 'sb-aktion-spielstand'}).find('span')['class']:
            self.card = 'Red'
        elif 'sb-gelbrot' in event_row.find('div', {'class': 'sb-aktion-spielstand'}).find('span')['class']:
            self.card = 'Second yellow'
        else:
            raise ValueError('Unidentified card classes: '+str(event_row.find('div', {'class': 'sb-aktion-spielstand'}).find('span')['class']))
        
    def __str__(self):
        if self.reason:
            return f"{self.minute_str}: {self.card} card: {self.booked_player} [{self.reason}]"
        else:
            return f"{self.minute_str}: {self.card} card: {self.booked_player}"

class MatchClub:
    def __init__(self, club_div):
        self.starters = {}
        self.subs = {}
        self.coach_name_id = club_div.find('tr', {'class':'bench-table__tr'}).find('a')['href'][1:].replace('/profil/trainer/','_')
        for starter in club_div.find_all('div', {'class': 'formation-player-container'}):
            player_name_id = player_anchor_to_name_id(starter.find('a'))
            self.starters[player_name_id] = MatchPlayer(player_name_id, tm_formation_position_to_position(starter))
        for sub in club_div.find('table').find_all('tr')[:-1]:
            player_name_id = player_anchor_to_name_id(sub.find('a'))
            self.subs[player_name_id] =  MatchPlayer(player_name_id, 'SUB')
    
    def print_formation(self):
        for starter in self.starters.keys():
            print(f"{self.starters[starter].starting_position}: {starter}")
        print(f"COA: {self.coach_name_id}")

class MatchPlayer:
    def __init__(self, player_name_id, starting_position):
        self.player_name_id = player_name_id
        self.starting_position = starting_position
        self.goals = []
        self.own_goals = []
        self.assists = []
        self.yellow_card = None
        self.second_yellow = None
        self.red_card = None
        self.sub_out = None
        self.sub_in = None
        self.shootout = None
        self.captain = None
        self.injury = None

