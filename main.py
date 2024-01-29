import pandas as pd
import requests
import seaborn as sns
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt


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


class Player:
    def __init__(self, name, team, points, rebounds, assists, mvp_probability):
        self.name = name
        self.team = team
        self.points = points
        self.rebounds = rebounds
        self.assists = assists
        self.mvp_probability = mvp_probability


def teams_standings(table):
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


def plot_teams_standings(teams, conference_name, ax):
    data = {
        'Team': [team.name.split()[-1] for team in teams],
        'Wins': [int(team.wins) for team in teams],
        'Losses': [int(team.losses) for team in teams]
    }

    df = pd.DataFrame(data)

    wins_colors = ['lightblue' for _ in range(len(df['Team']))]
    losses_colors = ['salmon' for _ in range(len(df['Team']))]

    for i in range(6, 10):
        wins_colors[i] = 'blue'
        losses_colors[i] = 'red'

    sns.set(style='white')
    ax.bar(range(len(df['Team'])), df['Wins'], color=wins_colors, label='Wins', width=0.5, align='center')
    ax.bar(range(len(df['Team'])), df['Losses'], color=losses_colors, label='Losses', width=0.5, align='edge')
    ax.set_title(f'{conference_name} Conference Standings')
    ax.set_ylabel('Games')
    ax.set_xticks(range(len(df['Team'])))
    ax.set_xticklabels(df['Team'], rotation=45, ha='right')
    ax.tick_params(axis='x', which='both', pad=5)
    ax.legend()


def mvp_tracker(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    mvp_award_tracker = soup.select('#players tbody tr')
    mvp_data = []

    for i, player_row in enumerate(mvp_award_tracker, start=1):
        player_data = player_row.find_all('td')

        player = Player(
            name=player_data[0].text,
            team=player_data[1].text,
            points=player_data[29].text,
            rebounds=player_data[23].text,
            assists=player_data[24].text,
            mvp_probability=float(player_data[31].text.rstrip('%'))
        )

        mvp_data.append(player)

        print(f'{i} {player.name}, {player.team}')
        print(f'{player.points} PPG, {player.rebounds} RPG, {player.assists} APG')
        print(f'MVP probability: {player.mvp_probability}%\n')

    return mvp_data


def plot_mvp_probabilities(mvp_data, ax):
    top_5_mvp_data = sorted(mvp_data, key=lambda x: x.mvp_probability, reverse=True)[:5]
    labels = [player.name.split()[-1] for player in top_5_mvp_data]
    probabilities = [player.mvp_probability for player in top_5_mvp_data]

    ax.axis('equal')
    ax.pie(x=probabilities, labels=labels, startangle=90, counterclock=False,
           wedgeprops=dict(width=0.4))
    ax.set_title('MVP Tracker - Probabilities')


def player_stats_total(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    player_name = soup.select_one('#meta div h1 span').text.strip()
    totals_table = soup.select('#totals tbody tr')
    player_stats_data = {
        'Player': player_name
    }

    for row in totals_table:
        season = row.select_one('th[data-stat="season"] a').text
        age = row.select_one('td[data-stat="age"]').text

        team_element = row.select_one('td[data-stat="team_id"] a')
        team = team_element.text if team_element else row.select_one('td[data-stat="team_id"]').text

        games = row.select_one('td[data-stat="g"]').text
        points = row.select_one('td[data-stat="pts"]').text
        rebounds = row.select_one('td[data-stat="trb"]').text
        assists = row.select_one('td[data-stat="ast"]').text

        season_data = {
            'Season': season,
            'Age': age,
            'Team': team,
            'Games': games,
            'Points': points,
            'Rebounds': rebounds,
            'Assists': assists
        }

        if season_data['Season'] not in player_stats_data:
            player_stats_data[season_data['Season']] = season_data

    print(f'{player_name}')
    for key, season_data in player_stats_data.items():
        if key == 'Player':
            continue
        print(f'Season {season_data["Season"]} in {season_data["Team"]}, {season_data["Games"]} games, '
              f'{season_data["Points"]} PTS, {season_data["Rebounds"]} TRB, {season_data["Assists"]} AST, '
              f'{season_data["Age"]} years old')

    return player_stats_data


def data_for_plot(player_stats_data):
    age = [data['Age'] for data in player_stats_data.values() if isinstance(data, dict)]
    points = [int(data['Points']) for data in player_stats_data.values() if isinstance(data, dict)]
    rebounds = [int(data['Rebounds']) for data in player_stats_data.values() if isinstance(data, dict)]
    assists = [int(data['Assists']) for data in player_stats_data.values() if isinstance(data, dict)]

    return age, points, rebounds, assists


def plot_player_stats(player_stats_data, ax):
    age, points, rebounds, assists = data_for_plot(player_stats_data)

    sns.set(style='dark')
    ax.plot(age, points, label='Points', marker='o', color='salmon')
    ax.plot(age, rebounds, label='Rebounds', marker='o', color='darkblue')
    ax.plot(age, assists, label='Assists', marker='o', color='orange')
    ax.set_title(f'{player_stats_data["Player"]} - Stats through years')
    ax.set_xlabel('Age')
    ax.set_ylabel('Total')
    ax.legend()


def plot_player_stats_changes(player_stats_data, ax):
    age, points, rebounds, assists = data_for_plot(player_stats_data)

    points_change = [points[i] - points[i - 1] if i > 0 else 0 for i in range(len(points))]
    rebounds_change = [rebounds[i] - rebounds[i - 1] if i > 0 else 0 for i in range(len(rebounds))]
    assists_change = [assists[i] - assists[i - 1] if i > 0 else 0 for i in range(len(assists))]

    sns.set(style='dark')
    ax.plot(age, points_change, '--', label='Points change')
    ax.plot(age, rebounds_change, '--', label='Rebounds change')
    ax.plot(age, assists_change, '--', label='Assists change')
    ax.set_title(f'{player_stats_data["Player"]} - Stats changes through years')
    ax.set_xlabel('Age')
    ax.set_ylabel('Change from previous year')
    ax.legend()


def is_response_successful(response):
    return response.status_code == 200


def main():
    urls = {
        'standings': 'https://www.basketball-reference.com/leagues/NBA_2024.html',
        'mvp_tracker': 'https://www.basketball-reference.com/friv/mvp.html',
        'player_stats': 'https://www.basketball-reference.com/players/j/jamesle01.html'
        # 'player_stats': 'https://www.basketball-reference.com/players/d/duranke01.html'
        # 'player_stats': 'https://www.basketball-reference.com/players/a/antetgi01.html'
    }

    responses = {key: requests.get(url) for key, url in urls.items()}

    if all(is_response_successful(response) for response in responses.values()):
        soup = BeautifulSoup(responses['standings'].text, 'html.parser')

        standings = soup.select('.section_wrapper.data_grid.standings_confs')
        west_table = standings[0].select_one('#confs_standings_W')
        east_table = standings[0].select_one('#confs_standings_E')

        print('Western Conference standings')
        west_teams = teams_standings(west_table)
        for team in west_teams:
            print(team)

        print('------------------------------------------------------------------------------')

        print('Eastern Conference standings')
        east_teams = teams_standings(east_table)
        for team in east_teams:
            print(team)

        print('------------------------------------------------------------------------------')
        print('MVP Tracker')
        mvp_data = mvp_tracker(urls['mvp_tracker'])
        print('------------------------------------------------------------------------------')

        player_stats = player_stats_total(urls['player_stats'])
        print('------------------------------------------------------------------------------')

        sns.set(style='whitegrid')
        fig_one, axes_one = plt.subplots(2, 2, figsize=(14, 10))

        plot_teams_standings(west_teams, 'Western', axes_one[0, 0])
        plot_teams_standings(east_teams, 'Eastern', axes_one[0, 1])
        plot_mvp_probabilities(mvp_data, axes_one[1, 0])

        plt.get_current_fig_manager().set_window_title('Hoops Insights')
        plt.tight_layout()
        plt.savefig('plots/first_figure.png')
        plt.show()

        sns.set(style='whitegrid')
        fig_two, axes_two = plt.subplots(1, 2, figsize=(12, 6))

        plot_player_stats(player_stats, axes_two[0])
        plot_player_stats_changes(player_stats, axes_two[1])

        plt.get_current_fig_manager().set_window_title('Hoops Insights')
        plt.tight_layout()
        plt.savefig('plots/second_figure.png')
        plt.show()
    else:
        print(f'Error')


if __name__ == "__main__":
    main()
