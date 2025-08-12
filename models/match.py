from bs4 import BeautifulSoup
from models.constants import HOST
from models.utils import tm_minute_span_to_str, tm_formation_position_to_position, player_anchor_to_name_id
from functools import total_ordering
from datetime import datetime
from zoneinfo import ZoneInfo

class Match:
    def __init__(self, match_id:str):
        from models.interface import CachedGet
        self.id = match_id
        self.html = CachedGet(f'{HOST}/spielbericht/index/spielbericht/{self.id}').content
        bs = BeautifulSoup(self.html, features="html.parser")
        self.match_events = []
        self.clubs = {}
        self.home_club = bs.find_all('div', {'class':'sb-team'})[0].find('a')['href'].split('/saison_id')[0][1:].replace('/startseite/verein/','_')
        self.away_club = bs.find_all('div', {'class':'sb-team'})[1].find('a')['href'].split('/saison_id')[0][1:].replace('/startseite/verein/','_')
        self.datetime_str = ', '.join(list(map(lambda x:x.strip(),bs.find('p', {'class':'sb-datum'}).text.split('|')))[1:])
        self.datetime = datetime.strptime(self.datetime_str, "%a, %m/%d/%y, %I:%M %p")
        self.datetime = self.datetime.replace(tzinfo=ZoneInfo("Europe/Berlin"))
        self.tournament_id = bs.find('a', {'class':'direct-headline__link'})['href'].split('/')[4]
        self.season = bs.find('a', {'class':'direct-headline__link'})['href'].split('/')[6]
        for section in bs.find_all('div', {'class': 'large-12 columns'}):
            if 'Referee' in section.text: # Match data section
                continue
            elif 'This match' in section.text: # Ghost? section
                continue
            elif 'Timeline' in section.text: # Timeline section
                continue
            elif 'Line-Ups' in section.find('h2').text.strip(): # Line-ups section
                self.clubs[self.home_club] = MatchClub(section.find_all('div', {'class': 'large-6'})[0])
                self.clubs[self.away_club] = MatchClub(section.find_all('div', {'class': 'large-6'})[1])
            elif 'Goals' in section.find('h2').text.strip(): # Goals section
                for event_row in section.find_all('div', {'class': 'sb-aktion'}):
                    goal = Goal(event_row)
                    self.match_events.append(goal)
                    goal.add_to_players(self)
            elif 'Substitutions' in section.find('h2').text.strip(): # Substitutions section
                for event_row in section.find_all('div', {'class': 'sb-aktion'}):
                    substitution = Substitution(event_row)
                    self.match_events.append(substitution)
                    substitution.add_to_players(self)
            elif 'Cards' in section.find('h2').text.strip(): # Bookings section
                for event_row in section.find_all('div', {'class': 'sb-aktion'}):
                    booking = Booking(event_row)
                    self.match_events.append(booking)
                    booking.add_to_players(self)
            elif 'Penalty shoot-out' in section.find('h2').text.strip(): # Shoot-out section
                continue
            elif 'Special events' in section.find('h2').text.strip(): # Special events section
                continue
            elif 'missed penalties' in section.find('h2').text.strip(): # Missed Penalties section
                continue
            elif 'Manager sanctions' in section.find('h2').text.strip(): # Manager sanctions section
                continue
            elif 'Transfers between each other' in section.find('h2').text.strip(): # Transfers between each other section
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
        else:
            self.half = 3
        self.main_player = player_anchor_to_name_id(event_row.find_all('div', {'class': 'sb-aktion-spielerbild'})[0].find('a'))

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
    
    def add_to_players(self, match:Match):
        for club in match.clubs.keys():
            if self.main_player in match.clubs[club].players:
                self.player_club = club

class Goal(MatchEvent):
    def __init__(self, event_row):
        super().__init__(event_row)
        self.goalscorer_name_id = self.main_player
        assistant_url = event_row.find('div', {'class': 'sb-aktion-aktion'}).find_all('a')[1]['href'] if len(event_row.find('div', {'class': 'sb-aktion-aktion'}).find_all('a')) == 2 else None
        self.assistant_name_id = assistant_url[1:].split('/saison')[0].replace('/leistungsdatendetails/spieler/', '_') if assistant_url else None
        goal_details_lines = event_row.find('div', {'class': 'sb-aktion-aktion'}).text.split('\n')
        self.goal_type = goal_details_lines[1].split(',')[1].strip() if len(goal_details_lines[1].split(',')) == 3 else 'Own-goal' if 'Own-goal' in event_row.text else None
        self.assist_type = goal_details_lines[2].split(',')[1].strip() if self.assistant_name_id and len(goal_details_lines[2].split(',')) == 3 else None
        self.scoreboard = event_row.find_all('div', {'class': 'sb-aktion-spielstand'})[0].text.strip()

    def __str__(self):
        goal_str = f"{self.goalscorer_name_id} ({self.goal_type})" if self.goal_type else self.goalscorer_name_id
        assist_str = f" Assist: {self.assistant_name_id} ({self.assist_type})" if self.assist_type else f" Assist: {self.assistant_name_id}" if self. assistant_name_id else ''
        return f"{self.minute_str}: Goal: {goal_str}{assist_str} [{self.scoreboard}]"
    
    def add_to_players(self, match:Match):
        super().add_to_players(match)
        if self.goal_type == 'Own-goal':
            match.clubs[self.player_club].players[self.goalscorer_name_id].own_goals.append(self.minute_str)
        else:
            match.clubs[self.player_club].players[self.goalscorer_name_id].goals.append(self.minute_str)
        if self.assistant_name_id:
            match.clubs[self.player_club].players[self.assistant_name_id].assists.append(self.minute_str)


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
    
    def add_to_players(self, match:Match):
        super().add_to_players(match)
        match.clubs[self.player_club].players[self.subbed_out_name_id].sub_out = self.minute_str
        match.clubs[self.player_club].players[self.subbed_in_name_id].sub_in = self.minute_str
        

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
    
    def add_to_players(self, match:Match):
        super().add_to_players(match)
        if self.card == 'Yellow':
             match.clubs[self.player_club].players[self.booked_player].yellow_card = self.minute_str
        elif self.card == 'Red':
             match.clubs[self.player_club].players[self.booked_player].red_card = self.minute_str
        elif self.card == 'Second yellow':
             match.clubs[self.player_club].players[self.booked_player].second_yellow = self.minute_str

class MatchClub:
    def __init__(self, club_div):
        self.players = {}
        self.club_name_id = club_div.find_all('a')[0]['href'].split('/saison_id')[0][1:].replace('/startseite/verein/','_')
        self.coach_name_id = club_div.find('tr', {'class':'bench-table__tr'}).find('a')['href'][1:].replace('/profil/trainer/','_')
        for starter in club_div.find_all('div', {'class': 'formation-player-container'}):
            player_name_id = player_anchor_to_name_id(starter.find('a'))
            self.players[player_name_id] = MatchPlayer(player_name_id, tm_formation_position_to_position(starter))
        for sub in club_div.find('table').find_all('tr')[:-1]:
            player_name_id = player_anchor_to_name_id(sub.find('a'))
            self.players[player_name_id] =  MatchPlayer(player_name_id, 'SUB')
    
    def print_formation(self):
        print('====================================')
        print(self.club_name_id)
        for starter in self.players.keys():
            if self.players[starter].starting_position == 'SUB':
                continue
            print(self.players[starter])
        print(f"Coach: {self.coach_name_id}")
        for starter in self.players.keys():
            if self.players[starter].starting_position != 'SUB' or self.players[starter].get_minutes() == 0:
                continue
            print(self.players[starter])

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

    def __str__(self):
        output = f"{self.player_name_id} [{self.starting_position} {self.get_minutes()}']"
        for goal in self.goals:
            output += f" ⚽{goal}'"
        for goal in self.own_goals:
            output += f" ❗⚽{goal}'"
        for assist in self.assists:
            output += f" 👟{assist}'"
        if self.yellow_card:
            output += f" 🟨{self.yellow_card}'"
        if self.second_yellow:
            output += f" 🟨🟥{self.second_yellow}'"
        if self.red_card:
            output += f" 🟥{self.red_card}'"
        if self.sub_out:
            output += f" ⬇️{self.sub_out}'"
        if self.sub_in:
            output += f" ⬆️{self.sub_in}'"
        return output
    
    def get_minutes(self):
        minutes = 90
        if self.starting_position == 'SUB':
            if self.sub_in:
                minutes -= int(self.sub_in.split('+')[0])-1
            else:
                return 0
        if self.sub_out:
            remaining = 90 - int(self.sub_out.split('+')[0])
            minutes -= remaining
        return minutes

        