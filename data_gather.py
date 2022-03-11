"""
NBA Data Gatherer

Program to produce two json objects that hold arrays of individual game data
over 5 seasons of the NBA. Game data tracked is teams who played, date of the
game, if the home team won or lost, home team ELO at the start of the game,
away team ELO at the start of the game, home team streak at the start of the game,
away team streak at the start of the game, home point differential at the start
of the game, and away team point differential at the start of the game. One json
object does not contain the names of the teams who played and the date the game
was played.

Written by Cole Pendergraft and Colton Lobdell

To install the basketball_reference_scraper that is required to run this code
just execute the following command in your terminal:
pip install basketball-reference-scraper

"""

from basketball_reference_scraper.seasons import get_schedule, get_standings
import json


"""============================ Helper Functions ============================"""
def win_prob(h_elo, a_elo):
    home_court = 100/400
    home = 10**(h_elo/400)
    away = 10**(a_elo/400)
    adv = 10**(home_court)
    denom = away + adv*home
    h_prob = (adv*home) /  denom
    a_prob = (away) / denom
    return h_prob, a_prob

def elo_k(mov, elo_diff):
    k = 20
    if mov>0:
        dependence = (mov + 3)**(0.8)/(7.5 + 0.006*(elo_diff))
    else:
        dependence = (-mov + 3)**(0.8)/(7.5 + 0.006*(-elo_diff))
    return k * dependence

def new_elo(h_pts, a_pts, h_elo, a_elo):
    ## probabilities
    h_prob, a_prob = win_prob(h_elo, a_elo)
    ## set s based on who won
    if(h_pts > a_pts):
        h_win = 1
        a_win = 0
    else:
        h_win = 0
        a_win = 1
    ## get k
    mov = h_pts - a_pts
    elo_diff = h_elo - a_elo
    k = elo_k(mov, elo_diff)
    ## update elo values
    h_elo = h_elo + k * (h_win - h_prob)
    a_elo = a_elo + k * (a_win - a_prob)
    return h_elo, a_elo

"""=========================================================================="""


# List of all teams in the NBA
team_list = [
'Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Chicago Bulls',
'Charlotte Hornets', 'Cleveland Cavaliers', 'Dallas Mavericks', 'Denver Nuggets',
'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat',
'Milwaukee Bucks', 'Minnesota Timberwolves', 'New Orleans Pelicans' ,
'New York Knicks', 'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers',
'Phoenix Suns', 'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs',
'Toronto Raptors','Utah Jazz', 'Washington Wizards'
]

# ELO transcends seasons, so to calculate ELO for 2016-2017 and onwards we need
# ELO from 2015-2016.
# This list also tracks point differential and team streak
# as the season goes on. Currently set to 0 because the start of new season
# sees the point differential and streak reset to 0
end_performance_2015_2016 = {
'Atlanta Hawks' : [1593, 0, 0],
'Boston Celtics' : [1552, 0, 0],
'Brooklyn Nets' : [1289, 0, 0],
'Chicago Bulls' : [1454, 0, 0],
'Charlotte Hornets' : [1559, 0, 0],
'Cleveland Cavaliers' : [1759, 0, 0],
'Dallas Mavericks' : [1503, 0, 0],
'Denver Nuggets' : [1427, 0, 0],
'Detroit Pistons' : [1494, 0, 0],
'Golden State Warriors' : [1756, 0, 0],
'Houston Rockets' : [1536, 0, 0],
'Indiana Pacers' : [1542, 0, 0],
'Los Angeles Clippers' : [1610, 0, 0],
'Los Angeles Lakers' : [1275, 0, 0],
'Memphis Grizzlies' : [1438, 0, 0],
'Miami Heat' : [1597, 0, 0],
'Milwaukee Bucks' : [1392, 0, 0],
'Minnesota Timberwolves' : [1411, 0, 0],
'New Orleans Pelicans' : [1374, 0, 0],
'New York Knicks' : [1384, 0, 0],
'Oklahoma City Thunder' : [1744, 0, 0],
'Orlando Magic' : [1437, 0, 0],
'Philadelphia 76ers' : [1203, 0, 0],
'Phoenix Suns' : [1356, 0, 0],
'Portland Trail Blazers' : [1611, 0, 0],
'Sacramento Kings' : [1425, 0, 0],
'San Antonio Spurs' : [1759, 0, 0],
'Toronto Raptors' : [1590, 0, 0],
'Utah Jazz' : [1539, 0, 0],
'Washington Wizards' : [1530, 0, 0]
}

# The 2016_2017 season elo dictionary starts out as a clone of the end elo from
# the previous season and is then adjusted for the start of the new season
performance_2016_2017 = end_performance_2015_2016.copy()
for team in team_list:
    # new elo (start of season)
    performance_2016_2017[team][0] = round(((performance_2016_2017[team][0]*0.75) + (0.25*1505)))

# Create Vistor, Vistor Points, Home, Home Points, and date lists from regular
#season schedule
schedule_2016_2017 = get_schedule(2017, playoffs=False)
visitor_list = schedule_2016_2017['VISITOR']
vpts_list = schedule_2016_2017['VISITOR_PTS']
home_list = schedule_2016_2017['HOME']
hpts_list = schedule_2016_2017['HOME_PTS']
date_list = schedule_2016_2017['DATE']

# Initialize two arrays that will hold the games for the season. One has the
# game title and date and one does not (stringless).
stats_2016_2017 = []
stringless_stats_2016_2017 = []

# Make game stat updates based on season performance
for i in range(0, len(schedule_2016_2017.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2016_2017[home_team][0]
    away_elo = performance_2016_2017[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2016_2017[home_team][1]
    apt_diff = performance_2016_2017[away_team][1]

    # streak for each team before game results
    h_streak = performance_2016_2017[home_team][2]
    a_streak = performance_2016_2017[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2016_2017.append(game)
    stringless_stats_2016_2017.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2016_2017[home_team][2] == 0) or (performance_2016_2017[home_team][2] < 0):
            performance_2016_2017[home_team][2] = 1
        if performance_2016_2017[home_team][2] > 0:
            performance_2016_2017[home_team][2] += 1

        if (performance_2016_2017[away_team][2] == 0) or (performance_2016_2017[away_team][2] < 0):
            performance_2016_2017[away_team][2] -= 1
        if performance_2016_2017[home_team][2] > 0:
            performance_2016_2017[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2016_2017[home_team][2] == 0) or (performance_2016_2017[home_team][2] < 0):
            performance_2016_2017[home_team][2] -= 1
        elif performance_2016_2017[home_team][2] > 0:
            performance_2016_2017[home_team][2] = -1

        if (performance_2016_2017[away_team][2] == 0) or (performance_2016_2017[away_team][2] < 0):
            performance_2016_2017[away_team][2] = 1
        elif performance_2016_2017[home_team][2] > 0:
            performance_2016_2017[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2016_2017[away_team][1] += a_dif
    performance_2016_2017[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2016_2017[away_team][0] = round(new_a_elo)
    performance_2016_2017[home_team][0] = round(new_h_elo)


## playoffs for 2016-2017
playoff_schedule_2016_2017 = get_schedule(2017, playoffs=True)

visitor_list = playoff_schedule_2016_2017['VISITOR']
vpts_list = playoff_schedule_2016_2017['VISITOR_PTS']
home_list = playoff_schedule_2016_2017['HOME']
hpts_list = playoff_schedule_2016_2017['HOME_PTS']
date_list = playoff_schedule_2016_2017['DATE']

for i in range(1231, 1231+len(playoff_schedule_2016_2017.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2016_2017[home_team][0]
    away_elo = performance_2016_2017[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2016_2017[home_team][1]
    apt_diff = performance_2016_2017[away_team][1]

    # streak for each team before game results
    h_streak = performance_2016_2017[home_team][2]
    a_streak = performance_2016_2017[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2016_2017.append(game)
    stringless_stats_2016_2017.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2016_2017[home_team][2] == 0) or (performance_2016_2017[home_team][2] < 0):
            performance_2016_2017[home_team][2] = 1
        if performance_2016_2017[home_team][2] > 0:
            performance_2016_2017[home_team][2] += 1

        if (performance_2016_2017[away_team][2] == 0) or (performance_2016_2017[away_team][2] < 0):
            performance_2016_2017[away_team][2] -= 1
        if performance_2016_2017[home_team][2] > 0:
            performance_2016_2017[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2016_2017[home_team][2] == 0) or (performance_2016_2017[home_team][2] < 0):
            performance_2016_2017[home_team][2] -= 1
        elif performance_2016_2017[home_team][2] > 0:
            performance_2016_2017[home_team][2] = -1

        if (performance_2016_2017[away_team][2] == 0) or (performance_2016_2017[away_team][2] < 0):
            performance_2016_2017[away_team][2] = 1
        elif performance_2016_2017[home_team][2] > 0:
            performance_2016_2017[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2016_2017[away_team][1] += a_dif
    performance_2016_2017[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2016_2017[away_team][0] = round(new_a_elo)
    performance_2016_2017[home_team][0] = round(new_h_elo)

"""=========================================================================="""

# The 2017_2018 season elo dictionary starts out as a clone of the end elo from
# the previous season and is then adjusted for the start of the new season
performance_2017_2018 = performance_2016_2017.copy()
for team in team_list:
    # new elo (start of season)
    performance_2017_2018[team][0] = round(((performance_2017_2018[team][0]*0.75) + (0.25*1505)))
    # reset point differential
    performance_2017_2018[team][1] = 0
    # reset streak
    performance_2017_2018[team][2] = 0

# Create Vistor, Vistor Points, Home, Home Points, and date lists from regular
#season schedule
schedule_2017_2018 = get_schedule(2018, playoffs=False)
visitor_list = schedule_2017_2018['VISITOR']
vpts_list = schedule_2017_2018['VISITOR_PTS']
home_list = schedule_2017_2018['HOME']
hpts_list = schedule_2017_2018['HOME_PTS']
date_list = schedule_2017_2018['DATE']

# Initialize two arrays that will hold the games for the season. One has the
# game title and date and one does not (stringless).
stats_2017_2018 = []
stringless_stats_2017_2018 = []

# Make game stat updates based on season performance
for i in range(0, len(schedule_2017_2018.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2017_2018[home_team][0]
    away_elo = performance_2017_2018[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2017_2018[home_team][1]
    apt_diff = performance_2017_2018[away_team][1]

    # streak for each team before game results
    h_streak = performance_2017_2018[home_team][2]
    a_streak = performance_2017_2018[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2017_2018.append(game)
    stringless_stats_2017_2018.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2017_2018[home_team][2] == 0) or (performance_2017_2018[home_team][2] < 0):
            performance_2017_2018[home_team][2] = 1
        if performance_2017_2018[home_team][2] > 0:
            performance_2017_2018[home_team][2] += 1

        if (performance_2017_2018[away_team][2] == 0) or (performance_2017_2018[away_team][2] < 0):
            performance_2017_2018[away_team][2] -= 1
        if performance_2017_2018[home_team][2] > 0:
            performance_2017_2018[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2017_2018[home_team][2] == 0) or (performance_2017_2018[home_team][2] < 0):
            performance_2017_2018[home_team][2] -= 1
        elif performance_2017_2018[home_team][2] > 0:
            performance_2017_2018[home_team][2] = -1

        if (performance_2017_2018[away_team][2] == 0) or (performance_2017_2018[away_team][2] < 0):
            performance_2017_2018[away_team][2] = 1
        elif performance_2017_2018[home_team][2] > 0:
            performance_2017_2018[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2017_2018[away_team][1] += a_dif
    performance_2017_2018[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2017_2018[away_team][0] = round(new_a_elo)
    performance_2017_2018[home_team][0] = round(new_h_elo)


## playoffs for 2017-2018
playoff_schedule_2017_2018 = get_schedule(2018, playoffs=True)

visitor_list = playoff_schedule_2017_2018['VISITOR']
vpts_list = playoff_schedule_2017_2018['VISITOR_PTS']
home_list = playoff_schedule_2017_2018['HOME']
hpts_list = playoff_schedule_2017_2018['HOME_PTS']
date_list = playoff_schedule_2017_2018['DATE']

for i in range(1231, 1231+len(playoff_schedule_2017_2018.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2017_2018[home_team][0]
    away_elo = performance_2017_2018[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2017_2018[home_team][1]
    apt_diff = performance_2017_2018[away_team][1]

    # streak for each team before game results
    h_streak = performance_2017_2018[home_team][2]
    a_streak = performance_2017_2018[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2017_2018.append(game)
    stringless_stats_2017_2018.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2017_2018[home_team][2] == 0) or (performance_2017_2018[home_team][2] < 0):
            performance_2017_2018[home_team][2] = 1
        if performance_2017_2018[home_team][2] > 0:
            performance_2017_2018[home_team][2] += 1

        if (performance_2017_2018[away_team][2] == 0) or (performance_2017_2018[away_team][2] < 0):
            performance_2017_2018[away_team][2] -= 1
        if performance_2017_2018[home_team][2] > 0:
            performance_2017_2018[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2017_2018[home_team][2] == 0) or (performance_2017_2018[home_team][2] < 0):
            performance_2017_2018[home_team][2] -= 1
        elif performance_2017_2018[home_team][2] > 0:
            performance_2017_2018[home_team][2] = -1

        if (performance_2017_2018[away_team][2] == 0) or (performance_2017_2018[away_team][2] < 0):
            performance_2017_2018[away_team][2] = 1
        elif performance_2017_2018[home_team][2] > 0:
            performance_2017_2018[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2017_2018[away_team][1] += a_dif
    performance_2017_2018[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2017_2018[away_team][0] = round(new_a_elo)
    performance_2017_2018[home_team][0] = round(new_h_elo)

"""=========================================================================="""

# The 2018_2019 season elo dictionary starts out as a clone of the end elo from
# the previous season and is then adjusted for the start of the new season
performance_2018_2019 = performance_2017_2018.copy()
for team in team_list:
    # new elo (start of season)
    performance_2018_2019[team][0] = round(((performance_2018_2019[team][0]*0.75) + (0.25*1505)))
    # reset point differential
    performance_2018_2019[team][1] = 0
    # reset streak
    performance_2018_2019[team][2] = 0

# Create Vistor, Vistor Points, Home, Home Points, and date lists from regular
#season schedule
schedule_2018_2019 = get_schedule(2019, playoffs=False)
visitor_list = schedule_2018_2019['VISITOR']
vpts_list = schedule_2018_2019['VISITOR_PTS']
home_list = schedule_2018_2019['HOME']
hpts_list = schedule_2018_2019['HOME_PTS']
date_list = schedule_2018_2019['DATE']

# Initialize two arrays that will hold the games for the season. One has the
# game title and date and one does not (stringless).
stats_2018_2019 = []
stringless_stats_2018_2019 = []

# Make game stat updates based on season performance
for i in range(0, len(schedule_2018_2019.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2018_2019[home_team][0]
    away_elo = performance_2018_2019[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2018_2019[home_team][1]
    apt_diff = performance_2018_2019[away_team][1]

    # streak for each team before game results
    h_streak = performance_2018_2019[home_team][2]
    a_streak = performance_2018_2019[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2018_2019.append(game)
    stringless_stats_2018_2019.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2018_2019[home_team][2] == 0) or (performance_2018_2019[home_team][2] < 0):
            performance_2018_2019[home_team][2] = 1
        if performance_2018_2019[home_team][2] > 0:
            performance_2018_2019[home_team][2] += 1

        if (performance_2018_2019[away_team][2] == 0) or (performance_2018_2019[away_team][2] < 0):
            performance_2018_2019[away_team][2] -= 1
        if performance_2018_2019[home_team][2] > 0:
            performance_2018_2019[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2018_2019[home_team][2] == 0) or (performance_2018_2019[home_team][2] < 0):
            performance_2018_2019[home_team][2] -= 1
        elif performance_2018_2019[home_team][2] > 0:
            performance_2018_2019[home_team][2] = -1

        if (performance_2018_2019[away_team][2] == 0) or (performance_2018_2019[away_team][2] < 0):
            performance_2018_2019[away_team][2] = 1
        elif performance_2018_2019[home_team][2] > 0:
            performance_2018_2019[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2018_2019[away_team][1] += a_dif
    performance_2018_2019[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2018_2019[away_team][0] = round(new_a_elo)
    performance_2018_2019[home_team][0] = round(new_h_elo)


## playoffs for 2018-2019
playoff_schedule_2018_2019 = get_schedule(2019, playoffs=True)

visitor_list = playoff_schedule_2018_2019['VISITOR']
vpts_list = playoff_schedule_2018_2019['VISITOR_PTS']
home_list = playoff_schedule_2018_2019['HOME']
hpts_list = playoff_schedule_2018_2019['HOME_PTS']
date_list = playoff_schedule_2018_2019['DATE']

for i in range(1231, 1231+len(playoff_schedule_2018_2019.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2018_2019[home_team][0]
    away_elo = performance_2018_2019[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2018_2019[home_team][1]
    apt_diff = performance_2018_2019[away_team][1]

    # streak for each team before game results
    h_streak = performance_2018_2019[home_team][2]
    a_streak = performance_2018_2019[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2018_2019.append(game)
    stringless_stats_2018_2019.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2018_2019[home_team][2] == 0) or (performance_2018_2019[home_team][2] < 0):
            performance_2018_2019[home_team][2] = 1
        if performance_2018_2019[home_team][2] > 0:
            performance_2018_2019[home_team][2] += 1

        if (performance_2018_2019[away_team][2] == 0) or (performance_2018_2019[away_team][2] < 0):
            performance_2018_2019[away_team][2] -= 1
        if performance_2018_2019[home_team][2] > 0:
            performance_2018_2019[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2018_2019[home_team][2] == 0) or (performance_2018_2019[home_team][2] < 0):
            performance_2018_2019[home_team][2] -= 1
        elif performance_2018_2019[home_team][2] > 0:
            performance_2018_2019[home_team][2] = -1

        if (performance_2018_2019[away_team][2] == 0) or (performance_2018_2019[away_team][2] < 0):
            performance_2018_2019[away_team][2] = 1
        elif performance_2018_2019[home_team][2] > 0:
            performance_2018_2019[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2018_2019[away_team][1] += a_dif
    performance_2018_2019[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2018_2019[away_team][0] = round(new_a_elo)
    performance_2018_2019[home_team][0] = round(new_h_elo)

"""=========================================================================="""

# The 2019_2020 season elo dictionary starts out as a clone of the end elo from
# the previous season and is then adjusted for the start of the new season
performance_2019_2020 = performance_2018_2019.copy()
for team in team_list:
    # new elo (start of season)
    performance_2019_2020[team][0] = round(((performance_2019_2020[team][0]*0.75) + (0.25*1505)))
    # reset point differential
    performance_2019_2020[team][1] = 0
    # reset streak
    performance_2019_2020[team][2] = 0

# Create Vistor, Vistor Points, Home, Home Points, and date lists from regular
#season schedule
schedule_2019_2020 = get_schedule(2020, playoffs=False)
visitor_list = schedule_2019_2020['VISITOR']
vpts_list = schedule_2019_2020['VISITOR_PTS']
home_list = schedule_2019_2020['HOME']
hpts_list = schedule_2019_2020['HOME_PTS']
date_list = schedule_2019_2020['DATE']

# Initialize two arrays that will hold the games for the season. One has the
# game title and date and one does not (stringless).
stats_2019_2020 = []
stringless_stats_2019_2020 = []

# Make game stat updates based on season performance
for i in range(0, len(schedule_2019_2020.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2019_2020[home_team][0]
    away_elo = performance_2019_2020[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2019_2020[home_team][1]
    apt_diff = performance_2019_2020[away_team][1]

    # streak for each team before game results
    h_streak = performance_2019_2020[home_team][2]
    a_streak = performance_2019_2020[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2019_2020.append(game)
    stringless_stats_2019_2020.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2019_2020[home_team][2] == 0) or (performance_2019_2020[home_team][2] < 0):
            performance_2019_2020[home_team][2] = 1
        if performance_2019_2020[home_team][2] > 0:
            performance_2019_2020[home_team][2] += 1

        if (performance_2019_2020[away_team][2] == 0) or (performance_2019_2020[away_team][2] < 0):
            performance_2019_2020[away_team][2] -= 1
        if performance_2019_2020[home_team][2] > 0:
            performance_2019_2020[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2019_2020[home_team][2] == 0) or (performance_2019_2020[home_team][2] < 0):
            performance_2019_2020[home_team][2] -= 1
        elif performance_2019_2020[home_team][2] > 0:
            performance_2019_2020[home_team][2] = -1

        if (performance_2019_2020[away_team][2] == 0) or (performance_2019_2020[away_team][2] < 0):
            performance_2019_2020[away_team][2] = 1
        elif performance_2019_2020[home_team][2] > 0:
            performance_2019_2020[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2019_2020[away_team][1] += a_dif
    performance_2019_2020[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2019_2020[away_team][0] = round(new_a_elo)
    performance_2019_2020[home_team][0] = round(new_h_elo)


## playoffs for 2019-2020
playoff_schedule_2019_2020 = get_schedule(2020, playoffs=True)

visitor_list = playoff_schedule_2019_2020['VISITOR']
vpts_list = playoff_schedule_2019_2020['VISITOR_PTS']
home_list = playoff_schedule_2019_2020['HOME']
hpts_list = playoff_schedule_2019_2020['HOME_PTS']
date_list = playoff_schedule_2019_2020['DATE']

for i in range(1060, 1060+len(playoff_schedule_2019_2020.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2019_2020[home_team][0]
    away_elo = performance_2019_2020[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2019_2020[home_team][1]
    apt_diff = performance_2019_2020[away_team][1]

    # streak for each team before game results
    h_streak = performance_2019_2020[home_team][2]
    a_streak = performance_2019_2020[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2019_2020.append(game)
    stringless_stats_2019_2020.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2019_2020[home_team][2] == 0) or (performance_2019_2020[home_team][2] < 0):
            performance_2019_2020[home_team][2] = 1
        if performance_2019_2020[home_team][2] > 0:
            performance_2019_2020[home_team][2] += 1

        if (performance_2019_2020[away_team][2] == 0) or (performance_2019_2020[away_team][2] < 0):
            performance_2019_2020[away_team][2] -= 1
        if performance_2019_2020[home_team][2] > 0:
            performance_2019_2020[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2019_2020[home_team][2] == 0) or (performance_2019_2020[home_team][2] < 0):
            performance_2019_2020[home_team][2] -= 1
        elif performance_2019_2020[home_team][2] > 0:
            performance_2019_2020[home_team][2] = -1

        if (performance_2019_2020[away_team][2] == 0) or (performance_2019_2020[away_team][2] < 0):
            performance_2019_2020[away_team][2] = 1
        elif performance_2019_2020[home_team][2] > 0:
            performance_2019_2020[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2019_2020[away_team][1] += a_dif
    performance_2019_2020[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2019_2020[away_team][0] = round(new_a_elo)
    performance_2019_2020[home_team][0] = round(new_h_elo)

"""=========================================================================="""

# The 2020_2021 season elo dictionary starts out as a clone of the end elo from
# the previous season and is then adjusted for the start of the new season
performance_2020_2021 = performance_2019_2020.copy()
for team in team_list:
    # new elo (start of season)
    performance_2020_2021[team][0] = round(((performance_2020_2021[team][0]*0.75) + (0.25*1505)))
    # reset point differential
    performance_2020_2021[team][1] = 0
    # reset streak
    performance_2020_2021[team][2] = 0

# Create Vistor, Vistor Points, Home, Home Points, and date lists from regular
#season schedule
schedule_2020_2021 = get_schedule(2021, playoffs=False)
visitor_list = schedule_2020_2021['VISITOR']
vpts_list = schedule_2020_2021['VISITOR_PTS']
home_list = schedule_2020_2021['HOME']
hpts_list = schedule_2020_2021['HOME_PTS']
date_list = schedule_2020_2021['DATE']

# Initialize two arrays that will hold the games for the season. One has the
# game title and date and one does not (stringless).
stats_2020_2021 = []
stringless_stats_2020_2021 = []

# Make game stat updates based on season performance
for i in range(0, len(schedule_2020_2021.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2020_2021[home_team][0]
    away_elo = performance_2020_2021[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2020_2021[home_team][1]
    apt_diff = performance_2020_2021[away_team][1]

    # streak for each team before game results
    h_streak = performance_2020_2021[home_team][2]
    a_streak = performance_2020_2021[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2020_2021.append(game)
    stringless_stats_2020_2021.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2020_2021[home_team][2] == 0) or (performance_2020_2021[home_team][2] < 0):
            performance_2020_2021[home_team][2] = 1
        if performance_2020_2021[home_team][2] > 0:
            performance_2020_2021[home_team][2] += 1

        if (performance_2020_2021[away_team][2] == 0) or (performance_2020_2021[away_team][2] < 0):
            performance_2020_2021[away_team][2] -= 1
        if performance_2020_2021[home_team][2] > 0:
            performance_2020_2021[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2020_2021[home_team][2] == 0) or (performance_2020_2021[home_team][2] < 0):
            performance_2020_2021[home_team][2] -= 1
        elif performance_2020_2021[home_team][2] > 0:
            performance_2020_2021[home_team][2] = -1

        if (performance_2020_2021[away_team][2] == 0) or (performance_2020_2021[away_team][2] < 0):
            performance_2020_2021[away_team][2] = 1
        elif performance_2020_2021[home_team][2] > 0:
            performance_2020_2021[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2020_2021[away_team][1] += a_dif
    performance_2020_2021[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2020_2021[away_team][0] = round(new_a_elo)
    performance_2020_2021[home_team][0] = round(new_h_elo)


## playoffs for 2020-2021
playoff_schedule_2020_2021 = get_schedule(2021, playoffs=True)

visitor_list = playoff_schedule_2020_2021['VISITOR']
vpts_list = playoff_schedule_2020_2021['VISITOR_PTS']
home_list = playoff_schedule_2020_2021['HOME']
hpts_list = playoff_schedule_2020_2021['HOME_PTS']
date_list = playoff_schedule_2020_2021['DATE']

for i in range(1231, 1231+len(playoff_schedule_2020_2021.index)):
    # teams in the game
    away_team = visitor_list[i]
    home_team = home_list[i]

    # create game title
    game_title = f'{away_team} at {home_team}'

    # generates the game date. For loop is used to remove unnecessary timestamp
    # data from the date. Probably over the top but I want pretty strings
    date = ''
    for j in range(0, 10):
        date = date + str(date_list[i])[j]

    # points by both teams
    apts = int(vpts_list[i])
    hpts = int(hpts_list[i])

    # check if home team won or lost game of interest
    if hpts > apts:
        hw = '1'
    else:
        hw = '0'

    # teams elos before game results
    home_elo = performance_2020_2021[home_team][0]
    away_elo = performance_2020_2021[away_team][0]

    # point differential for each team before game results
    hpt_diff = performance_2020_2021[home_team][1]
    apt_diff = performance_2020_2021[away_team][1]

    # streak for each team before game results
    h_streak = performance_2020_2021[home_team][2]
    a_streak = performance_2020_2021[away_team][2]

    # Game information
    # [teams that played, date played, '1' if home team won '0' otherwise,
    #home elo, away elo, hpt diff, apt diff, hstreak, astreak]
    game = [game_title, date, hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # For the file that does not have the game name and date
    game_stringless = [hw, home_elo, away_elo, hpt_diff, apt_diff, h_streak, a_streak]

    # Add games to their relevant statsheets
    stats_2020_2021.append(game)
    stringless_stats_2020_2021.append(game_stringless)

    # Update the streak for each team
    if hw == '1': # Home team won
        if (performance_2020_2021[home_team][2] == 0) or (performance_2020_2021[home_team][2] < 0):
            performance_2020_2021[home_team][2] = 1
        if performance_2020_2021[home_team][2] > 0:
            performance_2020_2021[home_team][2] += 1

        if (performance_2020_2021[away_team][2] == 0) or (performance_2020_2021[away_team][2] < 0):
            performance_2020_2021[away_team][2] -= 1
        if performance_2020_2021[home_team][2] > 0:
            performance_2020_2021[home_team][2] = -1

    elif hw == '0': # Home team lost
        if (performance_2020_2021[home_team][2] == 0) or (performance_2020_2021[home_team][2] < 0):
            performance_2020_2021[home_team][2] -= 1
        elif performance_2020_2021[home_team][2] > 0:
            performance_2020_2021[home_team][2] = -1

        if (performance_2020_2021[away_team][2] == 0) or (performance_2020_2021[away_team][2] < 0):
            performance_2020_2021[away_team][2] = 1
        elif performance_2020_2021[home_team][2] > 0:
            performance_2020_2021[home_team][2] += 1

    # point differential for each team
    h_dif = hpts - apts
    a_dif = apts - hpts

    # update point differential in performance tracker
    performance_2020_2021[away_team][1] += a_dif
    performance_2020_2021[home_team][1] += h_dif

    # calculate elo update based on game results
    new_h_elo, new_a_elo = new_elo(hpts, apts, home_elo, away_elo)

    # set updated elo in elo list for the next game played
    performance_2020_2021[away_team][0] = round(new_a_elo)
    performance_2020_2021[home_team][0] = round(new_h_elo)

"""=========================================================================="""

stats_array = [stats_2016_2017, stats_2017_2018, stats_2018_2019,
stats_2019_2020, stats_2020_2021]

json_str1 = json.dumps(stats_array)

with open("statsheet.json", "w") as outfile:
    outfile.write(json_str1)

stringless_stats_array = [stringless_stats_2016_2017, stringless_stats_2017_2018,
stringless_stats_2018_2019, stringless_stats_2019_2020, stringless_stats_2020_2021]

json_str2 = json.dumps(stringless_stats_array)

with open("statsheet_stringless.json", "w") as outfile:
    outfile.write(json_str2)
