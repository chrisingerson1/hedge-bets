import os
from dotenv import load_dotenv

import requests
from datetime import timezone
import datetime
import pytz

import math

load_dotenv()
API_KEY = os.getenv('API_KEY')
REGIONS = os.getenv('REGIONS')
ODDS_FORMAT = os.getenv('ODDS_FORMAT')
DATE_FORMAT = os.getenv('DATE_FORMAT')

LOG_ALL_RESULTS = os.getenv('LOG_ALL_RESULTS') == 'True'

INITIAL_MONEY = 1000

US_Books = ["barstool", "betonlineag", "betfair", "betmgm", "betrivers", "betus", "bovada",
            "circasports", "draftkings", "fanduel", "foxbet", "lowvig", "mybookieag", "pointsbetus",
            "sugarhouse", "superbook", "twinspires", "unibet_us", "williamhill_us", "wynnbet"]

MA_Books = ["barstool", "betmgm", "draftkings", "fanduel", "williamhill_us", "wynnbet"]

ALL_SPORTS_ML = [
    'americanfootball_ncaaf',
    'americanfootball_xfl',
    'aussierules_afl',
    'baseball_mlb',
    'basketball_euroleague',
    'basketball_nba',
    'basketball_ncaab',
    'cricket_ipl',
    'cricket_odi',
    'cricket_psl',
    'icehockey_nhl',
    'icehockey_sweden_allsvenskan',
    'icehockey_sweden_hockey_league',
    'mma_mixed_martial_arts',
    ]

ALL_SPORTS = [
    'americanfootball_ncaaf',
    'americanfootball_xfl',
    'aussierules_afl',
    'baseball_mlb',
    'basketball_euroleague',
    'basketball_nba',
    'basketball_ncaab',
    'cricket_ipl',
    'cricket_odi',
    'cricket_psl',
    'cricket_test_match',
    'icehockey_nhl',
    'icehockey_sweden_allsvenskan',
    'icehockey_sweden_hockey_league',
    'mma_mixed_martial_arts',
    'rugbyleague_nrl',
    'soccer_argentina_primera_division',
    'soccer_australia_aleague',
    'soccer_austria_bundesliga',
    'soccer_belgium_first_div',
    'soccer_chile_campeonato',
    'soccer_conmebol_copa_libertadores',
    'soccer_denmark_superliga',
    'soccer_efl_champ',
    'soccer_england_league1',
    'soccer_england_league2',
    'soccer_epl',
    'soccer_fa_cup',
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
    'soccer_usa_mls'
    ]

TOP_SPORTS_ML = [
    'baseball_mlb',
    'basketball_nba',
    'basketball_ncaab',
    'icehockey_nhl'
    ]
TOP_SPORTS = TOP_SPORTS_ML + ['soccer_epl']

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

def processML(book, outcomes, teams, bestBook, bestResults):
    homeIdx = 0 if teams['home'] == (outcomes[0])['name'] else 1
    awayIdx = 1 if homeIdx == 0 else 0
    odds = {'home': (outcomes[homeIdx])['price'],
            'away': (outcomes[awayIdx])['price']}

    if odds['home'] > (bestBook['home'])['odds']:
        bestBook['home'] = {'book': book, 'odds': odds['home']}

    if odds['away'] > (bestBook['away'])['odds']:
        bestBook['away'] = {'book': book, 'odds': odds['away']}

    bestResults['hasData'] = True

    bestResults['favorite'] = min((bestBook['home'])['odds'], (bestBook['away'])['odds'])
    bestResults['underdog'] = max((bestBook['home'])['odds'], (bestBook['away'])['odds'])

    return bestResults

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

def processSpread(currentBook, outcomes, teams, bestBook, bestResults, pointsList):
    homeIdx = 0 if teams['home'] == (outcomes[0])['name'] else 1
    awayIdx = 1 if homeIdx == 0 else 0

    pointsList['home'], (bestBook['home'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[homeIdx], pointsList['home'], (bestBook['home'])['pointsList'], True)
    pointsList['away'], (bestBook['away'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[awayIdx], pointsList['away'], (bestBook['away'])['pointsList'], True)

    (bestBook['home'])['bestLine'] = findBestLineSpread(bestBook['home'], pointsList['home'])
    (bestBook['away'])['bestLine'] = findBestLineSpread(bestBook['away'], pointsList['away'])

    bestResults['hasData'] = True

    return bestResults

def processTotal(currentBook, outcomes, bestBook, bestResults, pointsList):
    overIdx = 0 if (outcomes[0])['name'] == 'Over' else 1
    underIdx = 1 if overIdx == 0 else 1

    pointsList['over'], (bestBook['over'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[overIdx], pointsList['over'], (bestBook['over'])['pointsList'], False)
    pointsList['under'], (bestBook['under'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[underIdx], pointsList['under'], (bestBook['under'])['pointsList'], True)

    (bestBook['over'])['bestLine'] = findBestLineSpread(bestBook['over'], pointsList['over'])
    (bestBook['under'])['bestLine'] = findBestLineSpread(bestBook['under'], pointsList['under'])

    bestResults['hasData'] = True

    return bestResults

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

            bestResults = {'ml': {'hasData': False},
                           'spread': {'hasData': False},
                           'total': {'hasData': False}}

            pointsList = {'spread': {'home': [], 'away': []},
                          'total': {'over': [], 'under': []}}

            for book in game['bookmakers']:
                if book['key'] in booksList:
                    markets = book['markets']
                    for market in markets:
                        if market['key'] == 'h2h':
                            bestResults['ml'] = processML(book['title'], market['outcomes'], teams, bestBook['ml'], bestResults['ml'])
                        elif market['key'] == 'spreads':
                            bestResults['spread'] = processSpread(book['title'], market['outcomes'], teams, bestBook['spread'], bestResults['spread'], pointsList['spread'])
                        elif market['key'] == 'totals':
                            bestResults['totals'] = processTotal(book['title'], market['outcomes'], bestBook['total'], bestResults['total'], pointsList['total'])

            if ((bestResults['ml'])['hasData']):
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

            if ((bestResults['spread'])['hasData']):
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

            if ((bestResults['total'])['hasData']):
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

    return validResults

def main():
    scoresList = []
    for sport in TOP_SPORTS_ML:
        scoresList.append(getScoresResponse(sport, 'h2h'))
    for sport in TOP_SPORTS:
        scoresList.append(getScoresResponse(sport, 'spreads'))
        scoresList.append(getScoresResponse(sport, 'totals'))

    if len(scoresList) == 0:
        return

    validScoreResults = processScoreData(scoresList, US_Books, True)

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