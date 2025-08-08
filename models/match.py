from bs4 import BeautifulSoup
from models.constants import HOST
from models.utils import tm_minute_span_to_str

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
            elif 'This match' in section.text: # Ghost section
                continue
            elif 'Timeline' in section.text: # Timeline section
                continue
            elif 'Line-Ups' in section.find('h2').text.strip(): # Line-ups section
                continue
            elif 'Goals' in section.find('h2').text.strip(): # Goals section
                continue
            elif 'Substitutions' in section.find('h2').text.strip(): # Substitutions section
                continue
            elif 'Cards' in section.find('h2').text.strip(): # Bookings section
                continue
            elif 'Penalty shoot-out' in section.find('h2').text.strip(): # Shoot-out section
                continue
            else:
                raise ValueError(f"Unknown section: {section.find('h2').text.strip()}")

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
        main_player_url = event_row.find('div', {'class': 'sb-aktion-spielerbild'}).find('a')['href']
        main_player_name_id = main_player_url[1:].replace('/profil/spieler/', '_') 
        self.main_player = main_player_name_id

    def __str__(self):
        return f"{self.minute_str}: {self.main_player}"

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



