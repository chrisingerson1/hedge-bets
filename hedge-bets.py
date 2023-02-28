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

def findBestLineSpread(currentBook, outcome, bestSpread):
    points = outcome['point']

    if points > bestSpread['points']:
        bestSpread = {'book': currentBook,
                      'odds': outcome['price'],
                      'points': points}
    elif points == bestSpread['points']:
        bestSpread['book'] += ", " + currentBook

    return bestSpread

def addPointsValues(currentBook, outcome, pointList, bestBookLines):
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

    return pointList, bestBookLines

def processSpread(currentBook, outcomes, teams, bestBook, bestResults, pointsList):
    homeIdx = 0 if teams['home'] == (outcomes[0])['name'] else 1
    awayIdx = 1 if homeIdx == 0 else 0

    pointsList['home'], (bestBook['home'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[homeIdx], pointsList['home'], (bestBook['home'])['pointsList'])
    pointsList['away'], (bestBook['away'])['pointsList'] = \
        addPointsValues(currentBook, outcomes[awayIdx], pointsList['away'], (bestBook['away'])['pointsList'])

    bestResults['hasData'] = True

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
                                                         'points': float('-inf')}}}}

            bestResults = {'ml': {'hasData': False},
                           'spreads': {'hasData': False}}

            pointsList = {'home': [], 'away': []}

            for book in game['bookmakers']:
                if book['key'] in booksList:
                    markets = book['markets']
                    for market in markets:
                        #print (book['key'], market)
                        if market['key'] == 'h2h':
                            processML(book['title'], market['outcomes'], teams, bestBook['ml'], bestResults['ml'])
                        elif market['key'] == 'spreads':
                            processSpread(book['title'], market['outcomes'], teams, bestBook['spread'], bestResults['spreads'], pointsList)

            # prints out each game and their best odds with each book
            #print(game['sport_title'] + ": ", teams['home'], "(" + ((bestBook['ml'])['home'])['book'] + ")", ((bestBook['ml'])['home'])['odds'], "vs.", teams['away'], "(" + ((bestBook['ml'])['away'])['book'] + ")", ((bestBook['ml'])['away'])['odds'])
            #print('favorite', (bestResults['ml'])['favorite'], 'underdog', (bestResults['ml'])['underdog'])

            if ((bestResults['ml'])['hasData']):
                if (abs((bestResults['ml'])['favorite']) < (bestResults['ml'])['underdog']):
                    homeOdds = ((bestBook['ml'])['home'])['odds']
                    awayOdds = ((bestBook['ml'])['away'])['odds']
                    validResults.append(
                       {'sport': game['sport_title'],
                         'date': startTime,
                         'homeTeam': teams['home'],
                         'homeBook': ((bestBook['ml'])['home'])['book'],
                         'homeOdds': str(homeOdds) if homeOdds < 0 else '+' + str(homeOdds),
                         'awayTeam': teams['away'],
                         'awayBook': ((bestBook['ml'])['away'])['book'],
                         'awayOdds': str(awayOdds) if awayOdds < 0 else '+' + str(awayOdds),})

            if ((bestResults['spreads'])['hasData']):
                print (teams['home'], (bestBook['spread'])['home'])
                print (teams['away'], (bestBook['spread'])['away'])
                print()
                #homeOdds = ((bestBook['spread'])['home'])['odds']
                #homePoints = ((bestBook['spread'])['home'])['point']
                #awayOdds = ((bestBook['spread'])['away'])['odds']
                #awayPoints = ((bestBook['spread'])['away'])['point']
                #validResults.append(
                #    {'sport': game['sport_title'],
                #     'date': startTime,
                #     'homeTeam': teams['home'],
                #     'homeBook': ((bestBook['spread'])['home'])['book'],
                #     'homeOdds': str(homeOdds) if homeOdds < 0 else '+' + str(homeOdds),
                #     'homePoints': str(homePoints) if homePoints < 0 else '+' + str(homePoints),
                #     'awayTeam': teams['away'],
                #     'awayBook': ((bestBook['spread'])['away'])['book'],
                #     'awayOdds': str(awayOdds) if awayOdds < 0 else '+' + str(awayOdds),
                #     'awayPoints': str(awayPoints) if awayPoints < 0 else '+' + str(awayPoints),})

    return validResults

def main():
    sportsList = []
    sportsList.append(getResponse('basketball_nba', 'spreads'))
    #sportsList.append(getResponse('basketball_ncaab', 'h2h'))
    #sportsList.append(getResponse('baseball_mlb', 'h2h'))
    #sportsList.append(getResponse('icehockey_nhl', 'h2h'))

    requestsRemaining = sportsList[-1].headers['X-Requests-Remaining']

    validResults = processData(sportsList, US_Books, False)

    if (validResults):
        for res in validResults:
            if 'homePoints' in res.keys() and 'awayPoints' in res.keys():
                print(res['sport'] + " " + res['homeTeam'] + ":", res['homePoints'], res['homeOdds'], "(" + res['homeBook'] + ") vs. " + res['awayTeam'] + ":", res['awayPoints'], res['awayOdds'], "(" + res['awayBook'] + ")")
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
