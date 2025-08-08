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

ct = Match('4643228')
