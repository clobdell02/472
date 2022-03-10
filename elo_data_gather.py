"""
Program to compile and create a numpy array of numpy arrays that hold team ELO,
Wins, and Losses for each NBA team over the seasons 2016-2017, 2017-2018,
2018-2019, 2019-2020, and 2020-2021.

Written by Cole Pendergraft and Colton Lobdell

To install the basketball_reference_scraper that is required to run this code
just execute the following command in your terminal:
pip install basketball-reference-scraper
"""

from basketball_reference_scraper.seasons import get_schedule, get_standings
import numpy as np
import json
import pandas as pd

team_list = [ 'ATL', 'BOS', 'BRK', 'CHI', 'CHO', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC',
'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR',
'UTA', 'WAS']

# ELO transcends seasons, so to calculate ELO for 2016-2017 and onwards we need
# ELO from 2015-2016
# structure = { 'Team Name' : [ELO, Wins, Losses] }
stats_2015_2016 = {
'Atlanta Hawks' : [1593, 48, 34],
'Boston Celtics' : [1552, 48, 34],
'Brooklyn Nets' : [1289, 21, 61],
'Chicago Bulls' : [1454, 42, 40],
'Charlotte Hornets' : [1559, 48, 34],
'Cleveland Cavaliers' : [1759, 57, 25],
'Dallas Mavericks' : [1503, 42, 40],
'Denver Nuggets' : [1427, 33, 49],
'Detroit Pistons' : [1494, 44, 38],
'Golden State Warriors' : [1756, 73, 9],
'Houston Rockets' : [1536, 41, 41],
'Indiana Pacers' : [1542, 45, 37],
'Los Angeles Clippers' : [1610, 53, 29],
'Los Angeles Lakers' : [1275, 17, 65],
'Memphis Grizzlies' : [1438, 42, 40],
'Miami Heat' : [1597, 48, 34],
'Milwaukee Bucks' : [1392, 33, 49],
'Minnesota Timberwolves' : [1411, 29, 53],
'New Orleans Pelicans' : [1374, 30, 52],
'New York Knicks' : [1384, 32, 50],
'Oklahoma City Thunder' : [1744, 55, 27],
'Orlando Magic' : [1437, 35, 47],
'Philadelphia 76ers' : [1203, 10, 72],
'Phoenix Suns' : [1356, 23, 59],
'Portland Trail Blazers' : [1611, 44, 38],
'Sacramento Kings' : [1425, 33, 49],
'San Antonio Spurs' : [1759, 67, 15],
'Toronto Raptors' : [1590, 56, 26],
'Utah Jazz' : [1539, 40, 42],
'Washington Wizards' : [1530, 41, 41]
}

## helper functions:
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

# Create the next seasons (2016-2017) stats based on the previous
# Elo transends seasons
stats_2016_2017 = stats_2015_2016
for i in stats_2016_2017:
    # new elo (start of season)
    stats_2016_2017[i][0] = round(((stats_2016_2017[i][0]*0.75) + (0.25*1505)))
    # set wins to 0
    stats_2016_2017[i][1] = 0
    # set losses to 0
    stats_2016_2017[i][2] = 0

# Create Vistor, Vistor Points, Home, and Home Points lists from regular season schedule
schedule_2016_2017 = get_schedule(2017, playoffs=False)
visitor_list = schedule_2016_2017['VISITOR']
vpts_list = schedule_2016_2017['VISITOR_PTS']
home_list = schedule_2016_2017['HOME']
hpts_list = schedule_2016_2017['HOME_PTS']

#print(stats_2016_2017)
#print()

for i in range(0, len(schedule_2016_2017.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2016_2017[away_team][0]
        home_elo = stats_2016_2017[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2016_2017[away_team][0] = round(a_elo)
        stats_2016_2017[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2016_2017[away_team][2] += 1
            stats_2016_2017[home_team][1] += 1
        else:
            stats_2016_2017[away_team][1] += 1
            stats_2016_2017[home_team][2] += 1

#print(stats_2016_2017)
#print()

## playoffs for 2016-2017
playoff_schedule_2016_2017 = get_schedule(2017, playoffs=True)

visitor_list = playoff_schedule_2016_2017['VISITOR']
vpts_list = playoff_schedule_2016_2017['VISITOR_PTS']
home_list = playoff_schedule_2016_2017['HOME']
hpts_list = playoff_schedule_2016_2017['HOME_PTS']

for i in range(1231, 1231+len(playoff_schedule_2016_2017.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2016_2017[away_team][0]
        home_elo = stats_2016_2017[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2016_2017[away_team][0] = round(a_elo)
        stats_2016_2017[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2016_2017[away_team][2] += 1
            stats_2016_2017[home_team][1] += 1
        else:
            stats_2016_2017[away_team][1] += 1
            stats_2016_2017[home_team][2] += 1

#print(stats_2016_2017)
#print()

stats_2017_2018 = stats_2016_2017
for i in stats_2017_2018:
    # new elo (start of season)
    stats_2017_2018[i][0] = round(((stats_2017_2018[i][0]*0.75) + (0.25*1505)))
    # set wins to 0
    stats_2017_2018[i][1] = 0
    # set losses to 0
    stats_2017_2018[i][2] = 0

#print(stats_2017_2018)
#print()

# Create Vistor, Vistor Points, Home, and Home Points lists from regular season schedule
schedule_2017_2018 = get_schedule(2018, playoffs=False)
visitor_list = schedule_2017_2018['VISITOR']
vpts_list = schedule_2017_2018['VISITOR_PTS']
home_list = schedule_2017_2018['HOME']
hpts_list = schedule_2017_2018['HOME_PTS']

for i in range(0, len(schedule_2017_2018.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2017_2018[away_team][0]
        home_elo = stats_2017_2018[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2017_2018[away_team][0] = round(a_elo)
        stats_2017_2018[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2017_2018[away_team][2] += 1
            stats_2017_2018[home_team][1] += 1
        else:
            stats_2017_2018[away_team][1] += 1
            stats_2017_2018[home_team][2] += 1

#print(stats_2017_2018)
#print()

## playoffs for 2017-2018
playoff_schedule_2017_2018 = get_schedule(2018, playoffs=True)

visitor_list = playoff_schedule_2017_2018['VISITOR']
vpts_list = playoff_schedule_2017_2018['VISITOR_PTS']
home_list = playoff_schedule_2017_2018['HOME']
hpts_list = playoff_schedule_2017_2018['HOME_PTS']

for i in range(1231, 1231+len(playoff_schedule_2017_2018.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2017_2018[away_team][0]
        home_elo = stats_2017_2018[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2017_2018[away_team][0] = round(a_elo)
        stats_2017_2018[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2017_2018[away_team][2] += 1
            stats_2017_2018[home_team][1] += 1
        else:
            stats_2017_2018[away_team][1] += 1
            stats_2017_2018[home_team][2] += 1

#print(stats_2017_2018)
#print()

stats_2018_2019 = stats_2017_2018
for i in stats_2018_2019:
    # new elo (start of season)
    stats_2018_2019[i][0] = round(((stats_2018_2019[i][0]*0.75) + (0.25*1505)))
    # set wins to 0
    stats_2018_2019[i][1] = 0
    # set losses to 0
    stats_2018_2019[i][2] = 0

#print(stats_2018_2019)
#print()

# Create Vistor, Vistor Points, Home, and Home Points lists from regular season schedule
schedule_2018_2019 = get_schedule(2019, playoffs=False)
visitor_list = schedule_2018_2019['VISITOR']
vpts_list = schedule_2018_2019['VISITOR_PTS']
home_list = schedule_2018_2019['HOME']
hpts_list = schedule_2018_2019['HOME_PTS']

for i in range(0, len(schedule_2018_2019.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2018_2019[away_team][0]
        home_elo = stats_2018_2019[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2018_2019[away_team][0] = round(a_elo)
        stats_2018_2019[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2018_2019[away_team][2] += 1
            stats_2018_2019[home_team][1] += 1
        else:
            stats_2018_2019[away_team][1] += 1
            stats_2018_2019[home_team][2] += 1

#print(stats_2018_2019)
#print()

## playoffs for 2018-2019
playoff_schedule_2018_2019 = get_schedule(2019, playoffs=True)

visitor_list = playoff_schedule_2018_2019['VISITOR']
vpts_list = playoff_schedule_2018_2019['VISITOR_PTS']
home_list = playoff_schedule_2018_2019['HOME']
hpts_list = playoff_schedule_2018_2019['HOME_PTS']

for i in range(1231, 1231+len(playoff_schedule_2018_2019.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2018_2019[away_team][0]
        home_elo = stats_2018_2019[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2018_2019[away_team][0] = round(a_elo)
        stats_2018_2019[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2018_2019[away_team][2] += 1
            stats_2018_2019[home_team][1] += 1
        else:
            stats_2018_2019[away_team][1] += 1
            stats_2018_2019[home_team][2] += 1

#print(stats_2018_2019)
#print()

stats_2019_2020 = stats_2018_2019
for i in stats_2019_2020:
    # new elo (start of season)
    stats_2019_2020[i][0] = round(((stats_2019_2020[i][0]*0.75) + (0.25*1505)))
    # set wins to 0
    stats_2019_2020[i][1] = 0
    # set losses to 0
    stats_2019_2020[i][2] = 0

#print(stats_2018_2019)
#print()

# Create Vistor, Vistor Points, Home, and Home Points lists from regular season schedule
schedule_2019_2020 = get_schedule(2020, playoffs=False)
visitor_list = schedule_2019_2020['VISITOR']
vpts_list = schedule_2019_2020['VISITOR_PTS']
home_list = schedule_2019_2020['HOME']
hpts_list = schedule_2019_2020['HOME_PTS']

for i in range(0, len(schedule_2019_2020.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2019_2020[away_team][0]
        home_elo = stats_2019_2020[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2019_2020[away_team][0] = round(a_elo)
        stats_2019_2020[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2019_2020[away_team][2] += 1
            stats_2019_2020[home_team][1] += 1
        else:
            stats_2019_2020[away_team][1] += 1
            stats_2019_2020[home_team][2] += 1

#print(stats_2019_2020)
#print()

## playoffs for 2019-2020
playoff_schedule_2019_2020 = get_schedule(2020, playoffs=True)

visitor_list = playoff_schedule_2019_2020['VISITOR']
vpts_list = playoff_schedule_2019_2020['VISITOR_PTS']
home_list = playoff_schedule_2019_2020['HOME']
hpts_list = playoff_schedule_2019_2020['HOME_PTS']

for i in range(1060, 1060+len(playoff_schedule_2019_2020.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2019_2020[away_team][0]
        home_elo = stats_2019_2020[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2019_2020[away_team][0] = round(a_elo)
        stats_2019_2020[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2019_2020[away_team][2] += 1
            stats_2019_2020[home_team][1] += 1
        else:
            stats_2019_2020[away_team][1] += 1
            stats_2019_2020[home_team][2] += 1

#print(stats_2019_2020)
#print()

stats_2020_2021 = stats_2019_2020
for i in stats_2020_2021:
    # new elo (start of season)
    stats_2020_2021[i][0] = round(((stats_2020_2021[i][0]*0.75) + (0.25*1505)))
    # set wins to 0
    stats_2020_2021[i][1] = 0
    # set losses to 0
    stats_2020_2021[i][2] = 0

#print(stats_2018_2019)
#print()

# Create Vistor, Vistor Points, Home, and Home Points lists from regular season schedule
schedule_2020_2021 = get_schedule(2021, playoffs=False)
visitor_list = schedule_2020_2021['VISITOR']
vpts_list = schedule_2020_2021['VISITOR_PTS']
home_list = schedule_2020_2021['HOME']
hpts_list = schedule_2020_2021['HOME_PTS']

for i in range(0, len(schedule_2020_2021.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2020_2021[away_team][0]
        home_elo = stats_2020_2021[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2020_2021[away_team][0] = round(a_elo)
        stats_2020_2021[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2020_2021[away_team][2] += 1
            stats_2020_2021[home_team][1] += 1
        else:
            stats_2020_2021[away_team][1] += 1
            stats_2020_2021[home_team][2] += 1

#print(stats_2020_2021)
#print()

## playoffs for 2020-2021
playoff_schedule_2020_2021 = get_schedule(2021, playoffs=True)

visitor_list = playoff_schedule_2020_2021['VISITOR']
vpts_list = playoff_schedule_2020_2021['VISITOR_PTS']
home_list = playoff_schedule_2020_2021['HOME']
hpts_list = playoff_schedule_2020_2021['HOME_PTS']

for i in range(1231, 1231+len(playoff_schedule_2020_2021.index)):
        # teams in the game
        away_team = visitor_list[i]
        home_team = home_list[i]
        # points by both teams
        apts = int(vpts_list[i])
        hpts = int(hpts_list[i])
        # teams elos before game results
        away_elo = stats_2020_2021[away_team][0]
        home_elo = stats_2020_2021[home_team][0]
        # update stats based on game results
        h_elo, a_elo = new_elo(hpts, apts, home_elo, away_elo)
        # set updated elos
        stats_2020_2021[away_team][0] = round(a_elo)
        stats_2020_2021[home_team][0] = round(h_elo)
        # set updated wins Losses
        if(apts < hpts):
            stats_2020_2021[away_team][2] += 1
            stats_2020_2021[home_team][1] += 1
        else:
            stats_2020_2021[away_team][1] += 1
            stats_2020_2021[home_team][2] += 1

#print(stats_2020_2021)
#print()

# Create Numpy Arrays
data_2016_2017 = list(stats_2016_2017.items())
nparray_2016_2017 = np.array(data_2016_2017)

data_2017_2018 = list(stats_2017_2018.items())
nparray_2017_2018 = np.array(data_2017_2018)

data_2018_2019 = list(stats_2018_2019.items())
nparray_2018_2019 = np.array(data_2018_2019)

data_2019_2020 = list(stats_2019_2020.items())
nparray_2019_2020 = np.array(data_2019_2020)

data_2020_2021 = list(stats_2020_2021.items())
nparray_2020_2021 = np.array(data_2020_2021)

stats_array = np.array([nparray_2016_2017, nparray_2017_2018, nparray_2018_2019, nparray_2019_2020, nparray_2020_2021])

lists = stats_array.tolist()
json_str = json.dumps(lists)

with open("statsheet.json", "w") as outfile:
    outfile.write(json_str)
