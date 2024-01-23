import requests
from bs4 import BeautifulSoup

url = 'https://www.basketball-reference.com/leagues/NBA_2024.html'

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    standings = soup.select('.section_wrapper.data_grid.standings_confs')
    # print(standings)
    east_table = standings[0].select_one('#confs_standings_E')
    west_table = standings[0].select_one('#confs_standings_W')


    def process_table(table):
        rows = table.select('tbody tr.full_table')

        for row in rows:
            team_name = row.select_one('.left a').get_text()
            team_position = row.select_one('.seed').get_text(strip=True)[1:-1]
            wins = row.select_one('[data-stat="wins"]').get_text()
            losses = row.select_one('[data-stat="losses"]').get_text()

            print(f'{team_position} {team_name} - {wins}W {losses}L')


    print('Eastern Conference standings')
    process_table(east_table)

    print('---------------------------------------------------')

    print('Western Conference standings')
    process_table(west_table)
else:
    print(f'Error: {response.status_code}')
