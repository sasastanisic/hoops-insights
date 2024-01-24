import requests
from bs4 import BeautifulSoup


class Team:
    def __init__(self, name, position, wins, losses, win_loss_percentage, games_behind):
        self.name = name
        self.position = position
        self.wins = wins
        self.losses = losses
        self.win_loss_percentage = win_loss_percentage
        self.games_behind = games_behind

    def __str__(self):
        return (f'{self.position} {self.name} - {self.wins}W {self.losses}L - {self.win_loss_percentage:.1f}%, '
                f'{self.games_behind} GB')


def process_table(table):
    rows = table.select('tbody tr.full_table')
    teams = []

    for row in rows:
        team_name = row.select_one('.left a').get_text()
        team_position = row.select_one('.seed').get_text(strip=True)[1:-1]
        wins = row.select_one('[data-stat="wins"]').get_text()
        losses = row.select_one('[data-stat="losses"]').get_text()
        win_loss_percentage = float(row.select_one('[data-stat="win_loss_pct"]').get_text()) * 100
        games_behind = row.select_one('[data-stat="gb"]').get_text()

        team = Team(team_name, team_position, wins, losses, win_loss_percentage, games_behind)
        teams.append(team)

    return teams


def main():
    url = 'https://www.basketball-reference.com/leagues/NBA_2024.html'

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        standings = soup.select('.section_wrapper.data_grid.standings_confs')
        # print(standings)
        east_table = standings[0].select_one('#confs_standings_E')
        west_table = standings[0].select_one('#confs_standings_W')

        print('Eastern Conference standings')
        east_teams = process_table(east_table)
        for team in east_teams:
            print(team)

        print('-------------------------------------------------------')

        print('Western Conference standings')
        west_teams = process_table(west_table)
        for team in west_teams:
            print(team)
    else:
        print(f'Error: {response.status_code}')


if __name__ == "__main__":
    main()
