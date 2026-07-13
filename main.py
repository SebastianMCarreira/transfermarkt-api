import csv
from models.league import League
from models.interface import get_object, equal_images
from models.transfers import ClubAllTransfers
from models.club import Club
from models.match import Match
from models.player import Player
import warnings
from bs4 import MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module='bs4')

future_possible_rivals = [ Club('england_3299'), Club('spanien_3375'), Club('frankreich_3377') ]

match_test = Match('3964376')

# league = League('torneo-final_ARGC')
# for match_id in league.get_season_matches_ids('2024'):
#     match = Match(match_id)
#     for club in match.clubs.values():
#         club.print_formation()

messi = Player('lionel-messi_28003')
print(messi)

wc26_matches = [
    '4776617', # Algeria vs Argentina
    '4776641', # Austria vs Argentina
    '4776665', # Jordan vs Argentina
    '4776692', # Cabo Verde vs Argentina
    '4776701', # Egypt vs Argentina
    '4776705', # Switzerland vs Argentina
]

messi_players = []
for match_id in messi.get_all_matches():
    if match_id in wc26_matches:
        continue
    match = Match(match_id)
    # print(match)
    messi_club = match.get_club_from_player(messi.name_id)
    if messi_club is None:
        continue
    messi_matchplayer = match.clubs[messi_club].players[messi.name_id]
    if messi_matchplayer.get_minutes() == 0:
        continue
    for club in match.clubs.values():
        for player_id in club.players.keys():
            if player_id not in messi_players:
                messi_players.append(player_id)

print(f'Players who played with Messi: {len(messi_players)}')

new_messi_players = []
for wc_match in wc26_matches:
    match = Match(wc_match)
    # print(match)
    messi_club = match.get_club_from_player(messi.name_id)
    if messi_club is None:
        continue
    messi_matchplayer = match.clubs[messi_club].players[messi.name_id]
    if messi_matchplayer.get_minutes() == 0:
        continue
    for club in match.clubs.values():
        for player_id in club.players.keys():
            if match.clubs[club.club_name_id].players[player_id].get_minutes() == 0:
                continue
            if player_id in messi_players:
                player = Player(player_id)
                new_messi_players.append(f'{player.name} ({club.club_name_id})')

print(f'New players who played with Messi in WC26: {len(new_messi_players)}')
for new_player in new_messi_players:
    print(new_player)

for other in future_possible_rivals:
    for player in other.get_current_players():
        if player in messi_players:
            player_obj = Player(player)
            print(f'{player_obj.name} ({other.name})')