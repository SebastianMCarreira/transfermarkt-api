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

# club = Club('fc-sevilla-b-atletico-_8519')

match_test = Match('28094')

# league = League('torneo-final_ARGC')
# for match_id in league.get_season_matches_ids('2024'):
#     match = Match(match_id)
#     for club in match.clubs.values():
#         club.print_formation()

messi = Player('lionel-messi_28003')
print(messi)

messi_players = []
for match_id in messi.get_all_matches():
    match = Match(match_id)
    print(match)
    for club in match.clubs.values():
        for player_id in club.players.keys():
            if player_id not in messi_players:
                messi_players.append(player_id)

print(f'Players who played with Messi: {len(messi_players)}')
