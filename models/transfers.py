from models.constants import HOST
from models.utils import parse_name_id, parse_value, is_special_club
from bs4 import BeautifulSoup

SALE = 'SALE'
INTERNAL = 'INTERNAL'
RETURN = 'RETURN'
LOAN = 'LOAN'

class Transfer:
    def __init__(self, origin, destination, player, window, date, fee, transfer_type):
        self.origin = origin
        self.destination = destination
        self.player = player
        self.window = window
        self.date = date
        self.fee = fee
        self.transfer_type = transfer_type

    def __repr__(self):
        return f'{self.player} ({self.origin} -> {self.destination}) ${self.fee}'


class ClubAllTransfers:
    def __init__(self, name_id):
        from models.interface import CachedGet
        self.name_id = name_id
        self.url_name = name_id.split('_')[0]
        self.id = name_id.split('_')[1]
        self.html = CachedGet(f'https://{HOST}/{self.url_name}/alletransfers/verein/{self.id}').content
        bs = BeautifulSoup(self.html, features="html.parser")
        self.transfers = []
        for window in bs.find_all('div', {'class':'row'})[1:]:
            if 'Arrivals' not in window.find_all('div', recursive=False)[0].find('h2').text.strip():
                raise ValueError('Should be arrival')
            window_date = window.find_all('div', recursive=False)[0].find('h2').text.strip().split(' ')[1]
            arrivals = window.find_all('div', recursive=False)[0].find_all('tr')[1:-1]
            if len(window.find_all('div', recursive=False)) == 2:
                departures = window.find_all('div', recursive=False)[1].find_all('tr')[1:-1]
            else:
                departures = []
            for arrival in arrivals:
                if 'Loan fee:' in arrival.find_all('td')[3].text:
                    transfer_type = LOAN
                    transfer_value = parse_value(arrival.find_all('td')[3].text.split(':')[1])
                elif 'loan transfer' in arrival.find_all('td')[3].text:
                    transfer_type = LOAN
                    transfer_value = 0
                elif 'End of loan' in arrival.find_all('td')[3].text:
                    transfer_type = RETURN
                    transfer_value = 0
                elif 'free transfer' in arrival.find_all('td')[3].text or arrival.find_all('td')[3].text == '-':
                    transfer_type = SALE
                    transfer_value = 0
                else:
                    transfer_type = SALE
                    transfer_value = parse_value(arrival.find_all('td')[3].text)
                
                if is_special_club(arrival.find_all('td')[2].text):
                    origin = None
                else:
                    origin = parse_name_id(arrival.find_all('td')[2].find('a')['href'])
                self.transfers.append(Transfer(
                    origin,
                    self.name_id,
                    parse_name_id(arrival.find_all('td')[0].find('a')['href']),
                    window_date,
                    None,
                    transfer_value,
                    transfer_type
                ))
            for departure in departures:
                if 'Loan fee:' in departure.find_all('td')[3].text:
                    transfer_type = LOAN
                    transfer_value = parse_value(departure.find_all('td')[3].text.split(':')[1])
                elif 'loan transfer' in departure.find_all('td')[3].text:
                    transfer_type = LOAN
                    transfer_value = 0
                elif 'End of loan' in departure.find_all('td')[3].text:
                    transfer_type = RETURN
                    transfer_value = 0
                elif 'free transfer' in departure.find_all('td')[3].text or departure.find_all('td')[3].text == '-':
                    transfer_type = SALE
                    transfer_value = 0
                else:
                    transfer_type = SALE
                    transfer_value = parse_value(departure.find_all('td')[3].text)

                if is_special_club(departure.find_all('td')[2].text):
                    destination = None
                else:
                    destination = parse_name_id(departure.find_all('td')[2].find('a')['href'])
                self.transfers.append(Transfer(
                    self.name_id,
                    destination,
                    parse_name_id(departure.find_all('td')[0].find('a')['href']),
                    window_date,
                    None,
                    transfer_value,
                    transfer_type
                ))


