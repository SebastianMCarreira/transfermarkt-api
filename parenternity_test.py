from models.league import League
from models.interface import get_object

leagues = [
    'primera-division-r-f-e-f-grupo-ii_E3G2',
    'segunda-division-r-f-e-f-grupo-v_E4G5',
    'regionalliga-bayern_RLB3',
    'premier-league-2_GB21',
    'copa-lpf-proyeccion-final_CLPF',
    'cbf-brasileiro-u20_CB20'
]

for league_name_id in leagues:
    league = League(league_name_id)
    print('==================================================================')
    print(league.name)
    for club in league.current_clubs:
        club = get_object(club['club_url'])
        # club.find_parent()
        club.print_line()
