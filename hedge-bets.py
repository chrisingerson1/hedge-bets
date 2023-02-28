import os
from dotenv import load_dotenv

import requests
from datetime import timezone
import datetime
import pytz

load_dotenv()
API_KEY = os.getenv('API_KEY')
REGIONS = os.getenv('REGIONS')
ODDS_FORMAT = os.getenv('ODDS_FORMAT')

US_Books = ["barstool", "betonlineag", "betfair", "betmgm", "betrivers", "betus", "bovada",
            "circasports", "draftkings", "fanduel", "foxbet", "lowvig", "mybookieag", "pointsbetus",
            "sugarhouse", "superbook", "twinspires", "unibet_us", "williamhill_us", "wynnbet"]

MA_Books = ["barstool", "betmgm", "draftkings", "fanduel", "williamhill_us", "wynnbet"]

def getResponse(sport, markets):
    return requests.get('https://api.the-odds-api.com/v4/sports/' + sport + '/odds/',
                            params={
                                'api_key': API_KEY,
                                'regions': REGIONS,
                                'markets': markets,
                                'oddsFormat': ODDS_FORMAT})

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

def processData(sports, booksList, live):
    validResults = []
    currentTime = datetime.datetime.now(timezone.utc)

    for sport in sports:
        for game in sport.json():
            startTime = datetime.datetime.strptime(game['commence_time'],"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)

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
                if (abs((bestResults['ml'])['favorite']) < (bestResults['ml'])['underdog']):
                    homeOdds = ((bestBook['ml'])['home'])['odds']
                    awayOdds = ((bestBook['ml'])['away'])['odds']
                    validResults.append({
                        'sport': game['sport_title'],
                        'date': startTime,
                        'homeTeam': teams['home'],
                        'homeBook': ((bestBook['ml'])['home'])['book'],
                        'homeOdds': str(homeOdds) if homeOdds < 0 else '+' + str(homeOdds),
                        'awayTeam': teams['away'],
                        'awayBook': ((bestBook['ml'])['away'])['book'],
                        'awayOdds': str(awayOdds) if awayOdds < 0 else '+' + str(awayOdds),})

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
                    favorite = min((home[i])['odds'], (away[i])['odds'])
                    underdog = max((home[i])['odds'], (away[i])['odds'])

                    if abs(favorite) < underdog:
                        validResults.append({
                            'sport': game['sport_title'],
                            'date': startTime,
                            'homeTeam': teams['home'],
                            'homeBook': (home[i])['book'],
                            'homeOdds': str((home[i])['odds']) if (home[i])['odds'] < 0 else '+' + str((home[i])['odds']),
                            'homePoints': str((home[i])['points']) if (home[i])['points'] < 0 else '+' + str((home[i])['points']),
                            'awayTeam': teams['away'],
                            'awayBook': (away[i])['book'],
                            'awayOdds': str((away[i])['odds']) if (away[i])['odds'] < 0 else '+' + str((away[i])['odds']),
                            'awayPoints': str((away[i])['points']) if (away[i])['points'] < 0 else '+' + str((away[i])['points'])})

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
                    favorite = min((over[i])['odds'], (under[i])['odds'])
                    underdog = max((over[i])['odds'], (under[i])['odds'])

                    if abs(favorite) > underdog:
                        validResults.append({
                            'sport': game['sport_title'],
                            'date': startTime,
                            'homeTeam': teams['home'],
                            'overBook': (over[i])['book'],
                            'overOdds': str((over[i])['odds']) if (over[i])['odds'] < 0 else '+' + str((over[i])['odds']),
                            'overPoints': (over[i])['points'],
                            'awayTeam': teams['away'],
                            'underBook': (under[i])['book'],
                            'underOdds': str((under[i])['odds']) if (under[i])['odds'] < 0 else '+' + str((under[i])['odds']),
                            'underPoints': (under[i])['points'],
                        })

    return validResults

def main():
    sportsList = []
    sportsList.append(getResponse('basketball_nba', 'h2h,spreads,totals'))
    sportsList.append(getResponse('basketball_ncaab', 'h2h,spreads,totals'))
    sportsList.append(getResponse('baseball_mlb', 'h2h,spreads,totals'))
    sportsList.append(getResponse('icehockey_nhl', 'h2h,spreads,totals'))

    requestsRemaining = sportsList[-1].headers['X-Requests-Remaining']

    validResults = processData(sportsList, MA_Books, False)

    if (validResults):
        for res in validResults:
            if 'homePoints' in res.keys() and 'awayPoints' in res.keys():
                print(res['sport'] + " " + res['homeTeam'] + ":", res['homePoints'], res['homeOdds'], "(" + res['homeBook'] + ") vs. " + res['awayTeam'] + ":", res['awayPoints'], res['awayOdds'], "(" + res['awayBook'] + ")")
            elif 'overPoints' in res.keys() and 'underPoints' in res.keys():
                print(res['sport'], res['homeTeam'], "vs.", res['awayTeam'] + ": o" + str(res["overPoints"]), res["overOdds"], "(" + res["overBook"] + "), u" + str(res["underPoints"]), res["underOdds"], "(" + res["underBook"] + ")")
            else:
                print(res['sport'] + " " + res['homeTeam'] + ":", res['homeOdds'], "(" + res['homeBook'] + ") vs. " + res['awayTeam'] + ":", res['awayOdds'], "(" + res['awayBook'] + ")")
    else:
        print("No opportunities for hedge betting today")

    print("API calls remaining: " + requestsRemaining)

if __name__ == "__main__":
    main()

### RESPONSE JSON FORMAT ###
#id
#sport_key
#sport_title
#commence_time
#home_team
#away_team
#bookmakers
#   key
#   title
#   last_update
#   markets
#       key
#       last_update
#       outcomes
#           name
#           price
