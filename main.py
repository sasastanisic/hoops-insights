import requests
from bs4 import BeautifulSoup

url = 'https://www.basketball-reference.com/leagues/NBA_2024_standings.html'

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    east_teams = soup.select('#confs_standings_E > tbody > tr.full_table > .left')
    west_teams = soup.select('#confs_standings_W > tbody > tr.full_table > .left')

    for team in east_teams:
        team_name = team.find('a').get_text(strip=True)
        team_position = team.find('span', class_="seed").get_text(strip=True)
        team_position = team_position[1:-1]
        print(f"{team_position} {team_name}")

    print('--------------------------------------------')

    for team in west_teams:
        team_name = team.find('a').get_text(strip=True)
        team_position = team.find('span', class_="seed").get_text(strip=True)
        team_position = team_position[1:-1]
        print(f"{team_position} {team_name}")
else:
    print(f'Error: {response.status_code}')
