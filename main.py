import csv
from models.league import League
from models.interface import get_object, equal_images
from models.manager import AvailableManagers, Manager
from models.club import ClubTransferFlows, Club
import warnings
from bs4 import MarkupResemblesLocatorWarning
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning, module='bs4')

# club = Club('fc-sevilla-b-atletico-_8519')

cp = Club('rsc-internacional-fc_92878')
cp.find_parent()
cp.print_line()
print('bye')
