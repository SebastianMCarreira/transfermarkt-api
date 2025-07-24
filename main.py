import csv
from models.league import League
from models.interface import get_object, equal_images
from models.transfers import ClubAllTransfers
from models.club import Club
import warnings
from bs4 import MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module='bs4')

# club = Club('fc-sevilla-b-atletico-_8519')

ct = Club('club-atletico-river-plate_209')
ct2 = Club('cclub-atletico-river-plate-ii_14837')
print('bye')
