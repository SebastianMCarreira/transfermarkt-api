import csv
from models.league import League
from models.interface import get_object, equal_images
from models.transfers import ClubAllTransfers
from models.club import Club
from models.match import Match
import warnings
from bs4 import MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module='bs4')

# club = Club('fc-sevilla-b-atletico-_8519')

# match = Match('4643228')

league = League('torneo-final_ARGC')
for match_id in league.get_season_matches_ids('2024'):
    match = Match(match_id)
    for club in match.clubs.values():
        club.print_formation()
