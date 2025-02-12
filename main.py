import csv
from models.league import League
from models.interface import get_object

# m = Manager('pep-guardiola_5672')
# m = Manager('andoni-iraola_60677')
leagues = [
    'premier-league_GB1',
    'laliga_ES1',
    'ligue-1_FR1',
    'bundesliga_L1',
    'serie-a_IT1',
    'torneo-inicia_ARG1',
    'campeonato-brasileiro-serie-a_BRA1',
    'major-league-soccer_MLS1',
    'saudovskaa-pro-liga_SA1',
    'liga-nos_PO1',
    'eredivisie_NL1',
    'super-lig_TR1',
    'jupiler-pro-league_BE1',
    'super-league-1_GR1'
]


table = []
for l in leagues:
    league = League(l)
    for c in league.current_clubs:
        club = get_object(c['club_url'])
        manager = get_object(club.get_staff().manager['manager_url']) if club.get_staff().manager else None
        table.append({
            'league': league.name,
            'club': club.name,
            'manager': manager.name if manager else None,
            'position': (manager.player.main_position_cat if manager.get_player() else None) if manager else None,
            'ppm': manager.get_total_ppm() if manager else None,
            'matches': manager.get_total_matches() if manager else None
        })

print(table)
with open('output.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, table[0].keys())
    writer.writeheader()
    writer.writerows(table)
