import os
from dotenv import load_dotenv

import requests
from datetime import timezone
import datetime
import pytz

import math

from enum import Enum

from US_Books import *

class GameMode(Enum):
    HEDGE_BET = 1,
    BEST_LINES = 2,
    SHOW_ALL = 3

load_dotenv()
API_KEY = os.getenv('API_KEY')
REGIONS = os.getenv('REGIONS')
ODDS_FORMAT = os.getenv('ODDS_FORMAT')
DATE_FORMAT = os.getenv('DATE_FORMAT')

LOG_ALL_RESULTS = os.getenv('LOG_ALL_RESULTS') == 'True'
BEST_LINES = os.getenv('BEST_LINES') == 'True' and not LOG_ALL_RESULTS

INITIAL_MONEY = 1000

TOP_SPORTS_LIST = [
    'americanfootball_nfl',
    'americanfootball_ncaaf',
    'baseball_mlb',
    'basketball_nba',
    'basketball_ncaab',
    'icehockey_nhl',
    'mma_mixed_martial_arts',
    'soccer_epl',
]

TOP_SPORTS_PRINT = [
    "American Football - National Football League (NFL)",
    "American Football - NCAA Football",
    "Baseball          - Major League Baseball (MLB)",
    "Basketball        - National Basketball Association (NBA)",
    "Basketball        - NCAA Men's Basketball",
    "Ice Hockey        - National Hockey League (NHL)",
    "MMA               - Mixed Martial Arts",
    "Soccer            - English Premier League",
]

OTHER_SPORTS_LIST = [
    'americanfootball_cfl',
    'americanfootball_nfl_preseason',
    'americanfootball_xfl',
    'aussierules_afl',
    'baseball_mlb_preseason',
    'basketball_euroleague',
    'basketball_nba_preseason',
    'basketball_wnba',
    'cricket_asia_cup',
    'cricket_big_bash',
    'cricket_caribbean_premier_league',
    'cricket_icc_world_cup',
    'cricket_international_t20',
    'cricket_ipl',
    'cricket_odi',
    'cricket_psl',
    'cricket_test_match',
    'cricket_the_hundred',
    'icehockey_sweden_allsvenskan',
    'icehockey_sweden_hockey_league',
    'rugbyleague_nrl',
    'soccer_africa_cup_of_nations',
    'soccer_argentina_primera_division',
    'soccer_australia_aleague',
    'soccer_austria_bundesliga',
    'soccer_belgium_first_div',
    'soccer_brazil_campeonato',
    'soccer_brazil_serie_b',
    'soccer_chile_campeonato',
    'soccer_china_superleague',
    'soccer_conmebol_copa_libertadores',
    'soccer_denmark_superliga',
    'soccer_efl_champ',
    'soccer_england_efl_cup',
    'soccer_england_league1',
    'soccer_england_league2',
    'soccer_fa_cup',
    'soccer_fifa_world_cup',
    'soccer_finland_veikkausliiga',
    'soccer_france_ligue_one',
    'soccer_france_ligue_two',
    'soccer_germany_bundesliga',
    'soccer_germany_bundesliga2',
    'soccer_germany_liga3',
    'soccer_greece_super_league',
    'soccer_italy_serie_a',
    'soccer_italy_serie_b',
    'soccer_japan_j_league',
    'soccer_korea_kleague1',
    'soccer_league_of_ireland',
    'soccer_mexico_ligamx',
    'soccer_netherlands_eredivisie',
    'soccer_norway_eliteserien',
    'soccer_poland_ekstraklasa',
    'soccer_portugal_primeira_liga',
    'soccer_russia_premier_league',
    'soccer_spain_la_liga',
    'soccer_spain_segunda_division',
    'soccer_spl',
    'soccer_sweden_allsvenskan',
    'soccer_sweden_superettan',
    'soccer_switzerland_superleague',
    'soccer_turkey_super_league',
    'soccer_uefa_champs_league',
    'soccer_uefa_europa_conference_league',
    'soccer_uefa_europa_league',
    'soccer_uefa_nations_league',
    'soccer_usa_mls',
    'tennis_atp_aus_open_singles',
    'tennis_atp_french_open',
    'tennis_atp_us_open',
    'tennis_atp_wimbledon',
    'tennis_wta_aus_open_singles',
    'tennis_wta_french_open',
    'tennis_wta_us_open',
    'tennis_wta_wimbledon'
]

OTHER_SPORTS_PRINT = [
    "Canadian Football   - Canadian Football League (CFL)",
    "American Football   - National Football League Preseason (NFL Preseason)",
    "American Football   - Xtreme Football League (XFL)",
    "Australian Football - Australian Football League (AFL)",
    "Baseball            - Major League Baseball Preseason (MLB Spring Training)",
    "Basketball          - Euroleague",
    "Basketball          - National Basketball Association Preseason (NBA Preseason)",
    "Basketball          - Women's National Basketball Association (WNBA)",
    "Cricket             - Asia Cup",
    "Cricket             - Big Bash",
    "Cricket             - Caribbean Premier League",
    "Cricket             - Men's ICC World Cup",
    "Cricket             - Men's International Twenty20",
    "Cricket             - Indian Premier League",
    "Cricket             - One Day Internationals",
    "Cricket             - Pakistan Super League",
    "Cricket             - International Test Matches",
    "Cricket             - The Hundred",
    "Ice Hockey          - Allsvenskan (Sweden)",
    "Ice Hockey          - Swedish Hockey League",
    "Rugby               - National Rugby League (NRL)",
    "Soccer"
]

ALL_SPORTS_LIST = TOP_SPORTS_LIST + OTHER_SPORTS_LIST
ALL_SPORTS_PRINT = TOP_SPORTS_PRINT + OTHER_SPORTS_PRINT

def decimalOdds(odds):
    return 1 + 100/math.fabs(odds) if odds < 0 else 1 + odds/100.0

def calculateROI(oddsA, oddsB):
    oddsA_decimal = decimalOdds(oddsA)
    oddsB_decimal = decimalOdds(oddsB)
    oddsA_wager = round((oddsB_decimal / (oddsA_decimal + oddsB_decimal)) * INITIAL_MONEY, 2)
    oddsB_wager = round(INITIAL_MONEY - oddsA_wager, 2)
    ROI = round(((((oddsA_wager*oddsA_decimal) / float(INITIAL_MONEY)) - 1) * 100), 2)

    return oddsA_wager, oddsB_wager, ROI

def getScoresResponse(sport, markets):
    return requests.get('https://api.the-odds-api.com/v4/sports/' + sport + '/odds/',
                            params={
                                'api_key': API_KEY,
                                'regions': REGIONS,
                                'markets': markets,
                                'oddsFormat': ODDS_FORMAT,
                                'dateFormat': DATE_FORMAT})

def getEventResponse(sport, eventId, markets):
    return requests.get('https://api.the-odds-api.com/v4/sports/' + sport + '/events/' + eventId + '/odds/',
                            params={
                                'api_key': API_KEY,
                                'regions': REGIONS,
                                'markets': markets,
                                'oddsFormat': ODDS_FORMAT,
                                'dateFormat': DATE_FORMAT})

def processML(book, outcomes, teams, bestBook):
    homeIdx = 0 if teams['home'] == (outcomes[0])['name'] else 1
    awayIdx = 1 if homeIdx == 0 else 0
    odds = {'home': (outcomes[homeIdx])['price'],
            'away': (outcomes[awayIdx])['price']}

    if odds['home'] > (bestBook['home'])['odds']:
        bestBook['home'] = {'book': book, 'odds': odds['home']}

    if odds['away'] > (bestBook['away'])['odds']:
        bestBook['away'] = {'book': book, 'odds': odds['away']}

    return True

def findBestLineSpread(bestBook, pointsList):
    for line in range(len(bestBook['pointsList'])):
        if ((bestBook['pointsList'])[line])['points'] == pointsList[0]:
            bestBook['bestLine'] = (bestBook['pointsList'])[line]
    
    return bestBook['bestLine']

def addPointsValues(currentBook, outcome, pointList, bestBookLines, reverse):
    odds = outcome['price']
    points = outcome['point']

    if points in pointList:
        for line in range(len(bestBookLines)):
            if (bestBookLines[line])['points'] == points:
                if odds > (bestBookLines[line])['odds']:
                    bestBookLines[line] = {'book': currentBook,
                                           'odds': odds,
                                           'points': points}
                elif odds == (bestBookLines[line])['odds']:
                    (bestBookLines[line])['book'] += ", " + currentBook

    else:
        pointList.append(points)
        bestBookLines.append({'book': currentBook,
                              'odds': odds,
                              'points': points})

    pointList.sort(reverse=reverse)

    return pointList, bestBookLines

def processSpread(currentBook, outcomes, teams, bestBook, pointsList):
    homeIdx = 0 if teams['home'] == (outcomes[0])['name'] else 1
    awayIdx = 1 if homeIdx == 0 else 0

    pointsList['home'], (bestBook['home'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[homeIdx], pointsList['home'], (bestBook['home'])['pointsList'], True)
    pointsList['away'], (bestBook['away'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[awayIdx], pointsList['away'], (bestBook['away'])['pointsList'], True)

    (bestBook['home'])['bestLine'] = findBestLineSpread(bestBook['home'], pointsList['home'])
    (bestBook['away'])['bestLine'] = findBestLineSpread(bestBook['away'], pointsList['away'])

    return True

def processTotal(currentBook, outcomes, bestBook, pointsList):
    overIdx = 0 if (outcomes[0])['name'] == 'Over' else 1
    underIdx = 1 if overIdx == 0 else 1

    pointsList['over'], (bestBook['over'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[overIdx], pointsList['over'], (bestBook['over'])['pointsList'], False)
    pointsList['under'], (bestBook['under'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[underIdx], pointsList['under'], (bestBook['under'])['pointsList'], True)

    (bestBook['over'])['bestLine'] = findBestLineSpread(bestBook['over'], pointsList['over'])
    (bestBook['under'])['bestLine'] = findBestLineSpread(bestBook['under'], pointsList['under'])

    return True

def processScoreData(sports, booksList, live):
    validResults = []
    currentTime = datetime.datetime.now(timezone.utc)

    for sport in sports:
        for game in sport.json():
            startTime = datetime.datetime.strptime(game['commence_time'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)

            if currentTime > startTime and ~live:
                continue

            teams = {'home': game['home_team'], 'away': game['away_team']}

            bestBook = {'ml': {'home': {'book': '', 'odds': float('-inf')},
                               'away': {'book': '', 'odds': float('-inf')},},
                        'spread': {'home': {'pointsList': [],
                                            'bestLine': {'book': '',
                                                         'odds': float('-inf'),
                                                         'points': float('-inf')}},
                                   'away': {'pointsList': [],
                                            'bestLine': {'book': '',
                                                         'odds': float('-inf'),
                                                         'points': float('-inf')}}},
                        'total': {'over': {'pointsList': [],
                                            'bestLine': {'book': '',
                                                        'odds': float('-inf'),
                                                        'points': float('-inf')}},
                                  'under': {'pointsList': [],
                                            'bestLine': {'book': '',
                                                         'odds': float('-inf'),
                                                         'points': float('-inf')}}}}

            hasData = {'ml': False,
                       'spread': False,
                       'total': False}

            pointsList = {'spread': {'home': [], 'away': []},
                          'total': {'over': [], 'under': []}}

            for book in game['bookmakers']:
                if book['key'] in booksList:
                    markets = book['markets']
                    for market in markets:
                        if market['key'] == 'h2h':
                            hasData['ml'] = processML(book['title'], market['outcomes'], teams, bestBook['ml'])
                        elif market['key'] == 'spreads':
                            hasData['spread'] = processSpread(book['title'], market['outcomes'], teams, bestBook['spread'], pointsList['spread'])
                        elif market['key'] == 'totals':
                            hasData['total'] = processTotal(book['title'], market['outcomes'], bestBook['total'], pointsList['total'])

            if hasData['ml']:
                homeOdds = ((bestBook['ml'])['home'])['odds']
                awayOdds = ((bestBook['ml'])['away'])['odds']
                homeWager, awayWager, ROI = calculateROI(homeOdds, awayOdds)

                if ROI > 0 or LOG_ALL_RESULTS:
                    validResults.append({
                        'sport': game['sport_title'],
                        'date': startTime,
                        'homeTeam': teams['home'],
                        'homeBook': ((bestBook['ml'])['home'])['book'],
                        'homeOdds': str(homeOdds) if homeOdds < 0 else '+' + str(homeOdds),
                        'wagerA': '$' + str(homeWager),
                        'awayTeam': teams['away'],
                        'awayBook': ((bestBook['ml'])['away'])['book'],
                        'awayOdds': str(awayOdds) if awayOdds < 0 else '+' + str(awayOdds),
                        'wagerB': '$' + str(awayWager),
                        'ROI': ROI
                    })

            if hasData['spread']:
                if not BEST_LINES:
                    home = []
                    away = []
                    for team in bestBook['spread']:
                        for list in ((bestBook['spread'])[team])['pointsList']:
                            if team == 'home':
                                home.append(list)
                            elif team == 'away':
                                away.append(list)
                    for i in range(len(home)):
                        homeOdds = (home[i])['odds']
                        awayOdds = (away[i])['odds']
                        homeWager, awayWager, ROI = calculateROI(homeOdds, awayOdds)

                        if ROI > 0 or LOG_ALL_RESULTS:
                            validResults.append({
                                'sport': game['sport_title'],
                                'date': startTime,
                                'homeTeam': teams['home'],
                                'homeBook': (home[i])['book'],
                                'homeOdds': str(homeOdds) if homeOdds < 0 else '+' + str(homeOdds),
                                'homePoints': str((home[i])['points']) if (home[i])['points'] < 0 else '+' + str((home[i])['points']),
                                'wagerA': '$' + str(homeWager),
                                'awayTeam': teams['away'],
                                'awayBook': (away[i])['book'],
                                'awayOdds': str(awayOdds) if awayOdds < 0 else '+' + str(awayOdds),
                                'awayPoints': str((away[i])['points']) if (away[i])['points'] < 0 else '+' + str((away[i])['points']),
                                'wagerB': '$' + str(awayWager),
                                'ROI': ROI
                            })
                else:
                    homeBestLine = ((bestBook['spread'])['home'])['bestLine']
                    awayBestLine = ((bestBook['spread'])['away'])['bestLine']
                    validResults.append({
                        'sport': game['sport_title'],
                        'date': startTime,
                        'homeTeam': teams['home'],
                        'homeBook': homeBestLine['book'],
                        'homeOdds': str(homeBestLine['odds']) if homeBestLine['odds'] < 0 else '+' + str(homeBestLine['odds']),
                        'homePoints': str(homeBestLine['points']) if homeBestLine['points'] < 0 else '+' + str(homeBestLine['points']),
                        'awayTeam': teams['away'],
                        'awayBook': awayBestLine['book'],
                        'awayOdds': str(awayBestLine['odds']) if awayBestLine['odds'] < 0 else '+' + str(awayBestLine['odds']),
                        'awayPoints': str(awayBestLine['points']) if awayBestLine['points'] < 0 else '+' + str(awayBestLine['points']),
                        'ROI': 0
                    })

            if hasData['total']:
                if not BEST_LINES:
                    over = []
                    under = []
                    for opt in bestBook['total']:
                        for list in ((bestBook['total'])[opt])['pointsList']:
                            if opt == 'over':
                                over.append(list)
                            elif opt == 'under':
                                under.append(list)
                    for i in range(len(over)):
                        overOdds = (over[i])['odds']
                        underOdds = (under[i])['odds']
                        overWager, underWager, ROI = calculateROI(overOdds, underOdds)

                        if ROI > 0 or LOG_ALL_RESULTS:
                            validResults.append({
                                'sport': game['sport_title'],
                                'date': startTime,
                                'homeTeam': teams['home'],
                                'overBook': (over[i])['book'],
                                'overOdds': str(overOdds) if overOdds < 0 else '+' + str(overOdds),
                                'overPoints': (over[i])['points'],
                                'wagerA': '$' + str(overWager),
                                'awayTeam': teams['away'],
                                'underBook': (under[i])['book'],
                                'underOdds': str(underOdds) if underOdds < 0 else '+' + str(underOdds),
                                'underPoints': (under[i])['points'],
                                'wagerB': '$' + str(underWager),
                                'ROI': ROI
                            })
                else:
                    overBestLine = ((bestBook['total'])['over'])['bestLine']
                    underBestLine = ((bestBook['total'])['under'])['bestLine']
                    validResults.append({
                        'sport': game['sport_title'],
                        'date': startTime,
                        'homeTeam': teams['home'],
                        'overBook': overBestLine['book'],
                        'overOdds': str(overBestLine['odds']) if overBestLine['odds'] < 0 else '+' + str(overBestLine['odds']),
                        'overPoints': str(overBestLine['points']),
                        'awayTeam': teams['away'],
                        'underBook': underBestLine['book'],
                        'underOdds': str(underBestLine['odds']) if underBestLine['odds'] < 0 else '+' + str(underBestLine['odds']),
                        'underPoints': str(underBestLine['points']),
                        'ROI': 0
                    })

    return validResults

def main():
    print('*** Welcome to Beat the Bookie ***')
    # initialize variables to for bookmakers
    booksList = []
    selectedBooks = ""
    
    state = input("Please enter a two-letter state abbreviation, or type 'MANUAL' to manually select your books: ")
    if state != 'MANUAL':
        # user has provided a two-letter state to fetch the list of available books
        booksList = globals().get(state, "Please enter a valid 2-letter state abbreviation")
        if state != 'ALL_BOOKS':
            offshore = input("Would you like to include offshore books? Type 'y' or 'n': ")
            if offshore == 'y':
                booksList += OFFSHORE_BOOKS
        for i in range(len(booksList)):
            # create a text block that says which books we are using
            selectedBooks += Books_Print[booksList[i]] + ", "
    else:
        for i in range(len(Books_Print)):
            # print full list of books
            print(i+1, Books_Print[i])
        manual_books = input("Select which books you would like to load in, separated by commas: ")
        # separate user list from text string into list
        manual_books = manual_books.split(",")
        for b in manual_books:
            # convert list items to integers
            try:
                bookIdx = int(b)-1
                if bookIdx >= 0 and bookIdx <= len(Books_Print):
                    selectedBooks += Books_Print[bookIdx] + ", "
                    booksList.append(bookIdx)
                else:
                    print("Improper book index " + str(bookIdx+1) + ", skipping...")
            except ValueError:
                print("Improper value entered: " + "'" + b + "'" + ", skipping...")
    
    # sort the composite list of bookmakers by alphabetical order
    booksList.sort()

    # chop off the final ", "
    selectedBooks = selectedBooks[0:-2]
    print("List of books loaded:", selectedBooks)
    #for i in range(len(booksList)):
    #    print(Books_Print[booksList[i]])

    gameMode = input("Please select a game mode")

    scoresList = []
    #if not BEST_LINES:
        #for sport in TOP_SPORTS_LIST:
            #scoresList.append(getScoresResponse(sport, 'h2h'))
    #for sport in TOP_SPORTS_LIST:
    #    scoresList.append(getScoresResponse(sport, 'spreads'))
        #scoresList.append(getScoresResponse(sport, 'totals'))

    #if len(scoresList) == 0:
    #    return

    validScoreResults = processScoreData(scoresList, booksList, True)

    if (validScoreResults):
        for res in validScoreResults:
            if 'homePoints' in res.keys() and 'awayPoints' in res.keys():
                print(res['sport'], "~", res['homeTeam'] + ":", res['homePoints'], res['homeOdds'], "(" + res['homeBook'] + ") vs. " + res['awayTeam'] + ":", res['awayPoints'], res['awayOdds'], "(" + res['awayBook'] + ")")
            elif 'overPoints' in res.keys() and 'underPoints' in res.keys():
                print(res['sport'], "~", res['homeTeam'], "vs.", res['awayTeam'] + ": o" + str(res["overPoints"]), res["overOdds"], "(" + res["overBook"] + "), u" + str(res["underPoints"]), res["underOdds"], "(" + res["underBook"] + ")")
            else:
                print(res['sport'], "~", res['homeTeam'] + ":", res['homeOdds'], "(" + res['homeBook'] + ") vs. " + res['awayTeam'] + ":", res['awayOdds'], "(" + res['awayBook'] + ")")
            
            # print out how much money you should lay on each line and your projected ROI
            if res['ROI'] > 0:
                print("     ", res['wagerA'], "     ", res['wagerB'], "  *   ROI: " + str(res['ROI']) + "%")
    else:
        print("No opportunities for hedge betting today")

    requestsRemaining = scoresList[-1].headers['X-Requests-Remaining']
    print("API calls remaining:", int(float(requestsRemaining)))

if __name__ == "__main__":
    main()