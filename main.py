import csv
from models.league import League
from models.interface import get_object, equal_images
from models.transfers import ClubAllTransfers
import warnings
from bs4 import MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module='bs4')

# club = Club('fc-sevilla-b-atletico-_8519')

ct = ClubAllTransfers('club-atletico-river-plate_209')
print('bye')
