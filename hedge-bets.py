import datetime
import os
from dotenv import load_dotenv

import requests
import time

import math

from US_Books import *

# variable to store user selected game
SELECTED_GAME = 0

HEDGE_BET = 1
BEST_LINES = 2
SHOW_ALL = 3
LIVE_ONLY = 4

load_dotenv()
API_KEY = os.getenv('API_KEY')
ODDS_FORMAT = os.getenv('ODDS_FORMAT')
DATE_FORMAT = os.getenv('DATE_FORMAT')

INITIAL_MONEY = 100

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

TOP_SPORTS_SHORT = [
    "NFL",
    "NCAAF",
    "MLB",
    "NBA",
    "NCAAM",
    "NHL",
    "MMA",
    "EPL",
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
    'baseball_ncaa',
    'basketball_euroleague',
    'basketball_nba_preseason',
    'basketball_wnba',
    'boxing_boxing',
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
    'soccer_spl',
    'soccer_spain_la_liga',
    'soccer_spain_segunda_division',
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
    'tennis_wta_aus_open_singles',
    'tennis_atp_french_open',
    'tennis_wta_french_open',
    'tennis_atp_us_open',
    'tennis_wta_us_open',
    'tennis_atp_wimbledon',
    'tennis_wta_wimbledon'
]

OTHER_SPORTS_SHORT = [
    "CFL",
    "NFL Preseason",
    "XFL",
    "Australian Football League",
    "MLB Spring Training",
    "NCAA Baseball",
    "Euroleague",
    "NBA Preseason",
    "WNBA",
    "Boxing",
    "Asia Cup",
    "Big Bash",
    "Caribbean Premier League",
    "Men's ICC World Cup",
    "Men's International Twenty20",
    "Indian Premier League",
    "One Day Internationals",
    "Pakistan Super League",
    "International Test Matches",
    "The Hundred",
    "Allsvenskan",
    "Swedish Hockey League",
    "NRL",
    "Africa Cup of Nations",
    "Argentina - Primera División",
    "Australia - A-League",
    "Austrian - Bundesliga",
    "Belgium - First Division A",
    "Brazil - Série A",
    "Brazil - Série B",
    "Chile - Primera División",
    "China - Super League",
    "Copa Libertadores",
    "Denmark - Superliga",
    "EFL Championship",
    "EFL Cup",
    "England - League 1",
    "England - League 2",
    "FA Cup",
    "FIFA World Cup",
    "Finland - Veikkausliiga",
    "France - Ligue 1",
    "France - Ligue 2",
    "Germany - Bundesliga",
    "Germany - Bundesliga 2",
    "Germany - Liga 3",
    "Grece - Super League",
    "Italy - Serie A",
    "Italy - Serie B",
    "Japan - J League",
    "Korea - K League 1",
    "League of Ireland",
    "Mexico - Liga MX",
    "Netherlands - Eredivisie",
    "Norway - Eliteserien",
    "Poland - Ekstraklasa",
    "Portugal - Primeira Liga",
    "Russia - Premier League",
    "Scotland - Premiership",
    "Spain - La Liga",
    "Spain - La Liga 2",
    "Sweden - Allsvenskan",
    "Sweden - Superettan",
    "Switzerland - Superleague",
    "Turkey - Super League",
    "UEFA Champions League",
    "UEFA Europa Conference League",
    "UEFA Europa League",
    "UEFA Nations League",
    "Major League Soccer (MLS)",
    "Australian Open Men's Singles",
    "Australian Open Women's Singles",
    "French Open Men's Singles",
    "French Open Women's Singles",
    "US Open Men's Singles",
    "US Open Women's Singles",
    "Wimbledon Men's Singles",
    "Wimbledon Women's Singles",
]

OTHER_SPORTS_PRINT = [
    "American Football   - Canadian Football League (CFL)",
    "American Football   - National Football League Preseason (NFL Preseason)",
    "American Football   - Xtreme Football League (XFL)",
    "Australian Football - Australian Football League (AFL)",
    "Baseball            - Major League Baseball Preseason (MLB Spring Training)",
    "Baseball            - NCAA Baseball",
    "Basketball          - Euroleague",
    "Basketball          - National Basketball Association Preseason (NBA Preseason)",
    "Basketball          - Women's National Basketball Association (WNBA)",
    "Boxing",
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
    "Soccer              - Africa Cup of Nations",
    "Soccer              - Argentina - Primera División",
    "Soccer              - Australia - A-League",
    "Soccer              - Austrian - Bundesliga",
    "Soccer              - Belgium - First Division A",
    "Soccer              - Brazil - Série A",
    "Soccer              - Brazil - Série B",
    "Soccer              - Chile - Primera División",
    "Soccer              - China - Super League",
    "Soccer              - Copa Libertadores",
    "Soccer              - Denmark - Superliga",
    "Soccer              - EFL Championship",
    "Soccer              - EFL Cup",
    "Soccer              - England - League 1",
    "Soccer              - England - League 2",
    "Soccer              - FA Cup",
    "Soccer              - FIFA World Cup",
    "Soccer              - Finland - Veikkausliiga",
    "Soccer              - France - Ligue 1",
    "Soccer              - France - Ligue 2",
    "Soccer              - Germany - Bundesliga",
    "Soccer              - Germany - Bundesliga 2",
    "Soccer              - Germany - Liga 3",
    "Soccer              - Grece - Super League",
    "Soccer              - Italy - Serie A",
    "Soccer              - Italy - Serie B",
    "Soccer              - Japan - J League",
    "Soccer              - Korea - K League 1",
    "Soccer              - League of Ireland",
    "Soccer              - Mexico - Liga MX",
    "Soccer              - Netherlands - Eredivisie",
    "Soccer              - Norway - Eliteserien",
    "Soccer              - Poland - Ekstraklasa",
    "Soccer              - Portugal - Primeira Liga",
    "Soccer              - Russia - Premier League",
    "Soccer              - Scotland - Premiership",
    "Soccer              - Spain - La Liga",
    "Soccer              - Spain - La Liga 2",
    "Soccer              - Sweden - Allsvenskan",
    "Soccer              - Sweden - Superettan",
    "Soccer              - Switzerland - Superleague",
    "Soccer              - Turkey - Super League",
    "Soccer              - UEFA Champions League",
    "Soccer              - UEFA Europa Conference League",
    "Soccer              - UEFA Europa League",
    "Soccer              - UEFA Nations League",
    "Soccer              - Major League Soccer (MLS)",
    "Tennis              - Australian Open Men's Singles",
    "Tennis              - Australian Open Women's Singles",
    "Tennis              - French Open Men's Singles",
    "Tennis              - French Open Women's Singles",
    "Tennis              - US Open Men's Singles",
    "Tennis              - US Open Women's Singles",
    "Tennis              - Wimbledon Men's Singles",
    "Tennis              - Wimbledon Women's Singles",
]

ALL_SPORTS_LIST = TOP_SPORTS_LIST + OTHER_SPORTS_LIST
ALL_SPORTS_PRINT = TOP_SPORTS_PRINT + OTHER_SPORTS_PRINT
ALL_SPORTS_SHORT = TOP_SPORTS_SHORT + OTHER_SPORTS_SHORT

def decimalOdds(odds):
    return 1 + 100/math.fabs(odds) if odds < 0 else 1 + odds/100.0

def calculateROI_2way(oddsA, oddsB):
    oddsA_decimal = decimalOdds(oddsA)
    oddsB_decimal = decimalOdds(oddsB)
    oddsA_wager = (oddsB_decimal / (oddsA_decimal + oddsB_decimal)) * INITIAL_MONEY
    oddsB_wager = INITIAL_MONEY - oddsA_wager
    ROI = ((((oddsA_wager*oddsA_decimal) / float(INITIAL_MONEY)) - 1) * 100)

    return round(oddsA_wager, 2), round(oddsB_wager, 2), round(ROI, 2)

def calculateROI_3way(oddsA, oddsB, oddsC):
    oddsA_decimal = decimalOdds(oddsA)
    oddsB_decimal = decimalOdds(oddsB)
    oddsC_decimal = decimalOdds(oddsC)
    oddsA_wager = INITIAL_MONEY / (1 + (oddsA_decimal/oddsB_decimal) + (oddsA_decimal/oddsC_decimal))
    oddsB_wager = INITIAL_MONEY / (1 + (oddsB_decimal/oddsA_decimal) + (oddsB_decimal/oddsC_decimal))
    oddsC_wager = (INITIAL_MONEY - oddsA_wager - oddsB_wager)
    ROI = ((((oddsA_wager*oddsA_decimal) / float(INITIAL_MONEY)) - 1) * 100)

    return round(oddsA_wager, 2), round(oddsB_wager, 2), round(oddsC_wager, 2), round(ROI, 2)

def getActiveSports():
    activeSports = []
    response = requests.get('https://api.the-odds-api.com/v4/sports/',
                                params={
                                    'api_key': API_KEY
                                })
    for sport in response.json():
        activeSports.append(sport['key'])

    return activeSports

def getScoresResponse(sport, regions, markets):
    return requests.get('https://api.the-odds-api.com/v4/sports/' + sport + '/odds/',
                            params={
                                'api_key': API_KEY,
                                'regions': regions,
                                'markets': markets,
                                'oddsFormat': ODDS_FORMAT,
                                'dateFormat': DATE_FORMAT})

def getLiveEvents(markets):
    return getScoresResponse('upcoming', markets)

# strip out spaces and comma delimit user input
def delimitInput(input, inputList, masterList, isSportsList, activeSports = []):
    selected = ""
    input = input.replace(" ", "").split(",")
    for i in input:
        if i.isdigit():
            # convert list items to integers in order to index the master list
            idx = int(i)-1
            if idx >= 0 and idx <= len(masterList):
                if isSportsList:
                    selected += ALL_SPORTS_SHORT[idx] + ", "
                    if masterList[idx] in activeSports:
                        inputList.append(masterList[idx])
                else:
                    selected += masterList[idx] + ", "
                    inputList.append(idx)
                
            else:
                print("Improper index " + str(idx+1) + ", skipping...")
        else:
            print("Improper value entered: '" + i + "', skipping...")

    # sort the composite list by alphabetical order
    inputList.sort()

    # chop off the final ", "
    selected = selected[0:-2]
    return selected

def extractData(books, event):
    booksList = []
    for book in books:
        booksList.append(Books[book])
    
    currentTime = time.time()

    # extract event data
    eventId = event['id']
    sport = event['sport_title']
    startTime = event['commence_time']
    homeTeam = event['home_team']
    awayTeam = event['away_team']
    bookData = {'h2h': {'book': [], 'lastUpdate': [], 'homePrice': [], 'awayPrice': [], 'drawPrice': []},
                'spreads': {'book': [], 'lastUpdate': [], 'homePoint': [], 'homePrice': [], 'awayPoint': [], 'awayPrice': []},
                'totals': {'book': [], 'lastUpdate': [], 'overPoint': [], 'overPrice': [], 'underPoint': [], 'underPrice': []}}
    
    isLive = True if currentTime > startTime else False

    for b in event['bookmakers']:
        bookKey = b['key']
        if bookKey in booksList:
            markets = b['markets']
            for market in markets:
                marketKey = market['key']
                # William Hill is more commonly known as Caesars Sportsbook
                (bookData[marketKey])['book'].append(b['title'] if b['title'] != "William Hill (US)" else "Caesars")
                (bookData[marketKey])['lastUpdate'].append(int(round(currentTime - b['last_update'], 0)))
            
                outcomes = market['outcomes']
                # Orient the home, away, and draw outcome
                idx1 = idx2 = idx3 = -1
                for outcomeIdx in range(len(outcomes)):
                    if (outcomes[outcomeIdx])['name'] == homeTeam or (outcomes[outcomeIdx])['name'] == 'Over':
                        idx1 = outcomeIdx
                    elif (outcomes[outcomeIdx])['name'] == awayTeam or (outcomes[outcomeIdx])['name'] == 'Under':
                        idx2 = outcomeIdx
                    elif (outcomes[outcomeIdx])['name'] == 'Draw':
                        idx3 = outcomeIdx
                if idx1 < 0 or idx2 < 0:
                    print("ERROR: Mismatched team names")
                    continue

                if marketKey == 'h2h':
                    (bookData[marketKey])['homePrice'].append((outcomes[idx1])['price'])
                    (bookData[marketKey])['awayPrice'].append((outcomes[idx2])['price'])
                    if idx3 > 0:
                        (bookData[marketKey])['drawPrice'].append((outcomes[idx3])['price'])
                
                elif marketKey == 'spreads':
                    (bookData[marketKey])['homePoint'].append((outcomes[idx1])['point'])
                    (bookData[marketKey])['homePrice'].append((outcomes[idx1])['price'])
                    (bookData[marketKey])['awayPoint'].append((outcomes[idx2])['point'])
                    (bookData[marketKey])['awayPrice'].append((outcomes[idx2])['price'])

                elif marketKey == 'totals':
                    (bookData[marketKey])['overPoint'].append((outcomes[idx1])['point'])
                    (bookData[marketKey])['overPrice'].append((outcomes[idx1])['price'])
                    (bookData[marketKey])['underPoint'].append((outcomes[idx2])['point'])
                    (bookData[marketKey])['underPrice'].append((outcomes[idx2])['price'])

    return eventId, sport, datetime.datetime.fromtimestamp(startTime), isLive, homeTeam, awayTeam, bookData

def findBestMLIdx(bookData, key, bestVal, idx, i):
    if len(bookData[key]) > i:
        if (bookData[key])[i] > bestVal:
            bestVal = (bookData[key])[i]
            idx = i
    return bestVal, idx

def bestLinesML(bookData):
    numScores = len(bookData['book'])
    bestHome = bestAway = bestDraw = -math.inf
    homeIdx = awayIdx = drawIdx = -1
    for i in range(numScores):
        bestHome, homeIdx = findBestMLIdx(bookData, 'homePrice', bestHome, homeIdx, i)
        bestAway, awayIdx = findBestMLIdx(bookData, 'awayPrice', bestAway, awayIdx, i)
        bestDraw, drawIdx = findBestMLIdx(bookData, 'drawPrice', bestDraw, drawIdx, i)
    
    return homeIdx, bestHome, awayIdx, bestAway, drawIdx, bestDraw

# if SELECTED_MODE is HEDGE BET
def hedge(books, sports, regions, markets):
    for sport in sports:
        sportData = getScoresResponse(sport, regions, markets).json()

        for event in sportData:
            eventID, sportID, startTime, isLive, homeTeam, awayTeam, bookData = extractData(books, event)
            
            # Find best lines
            homeIdx, bestHome, awayIdx, bestAway, drawIdx, bestDraw = bestLinesML(bookData['h2h'])
            if homeIdx < 0 or awayIdx < 0:
                continue

            printStr = f"{sportID} ~ {startTime}: {homeTeam} {bestHome if bestHome < 0 else '+' + str(bestHome)} ({((bookData['h2h'])['book'])[homeIdx]}) vs. {awayTeam} {bestAway if bestAway < 0 else '+' + str(bestAway)} ({((bookData['h2h'])['book'])[awayIdx]})"
            if isLive:
                printStr = "!! LIVE !! - " + printStr

            if drawIdx < 0:
                a, b, ROI = calculateROI_2way(bestHome, bestAway)
                if ROI > 0:
                    print(f"{printStr} ROI: {ROI}%")
            else:
                printStr += f", Draw {bestDraw if bestDraw < 0 else '+' + str(bestDraw)} ({((bookData['h2h'])['book'])[drawIdx]})"
                a, b, c, ROI = calculateROI_3way(bestHome, bestAway, bestDraw)
                if ROI > 0:
                    print(f"{printStr} ROI: {ROI}%")

# if SELECTED_MODE is BEST LINES
def bestLines(books, sports, regions, markets):
    for sport in sports:
        sportData = getScoresResponse(sport, regions, markets).json()

        for event in sportData:
            eventID, sportID, startTime, homeTeam, awayTeam, bookData = extractData(books, event)

            # Find best lines
            homeIdx, bestHome, awayIdx, bestAway, drawIdx, bestDraw = bestLinesML(bookData['h2h'])
            if homeIdx < 0 or awayIdx < 0:
                continue

            if drawIdx < 0:
                print(sportID, startTime, homeTeam, bestHome, ((bookData['h2h'])['book'])[homeIdx], awayTeam, bestAway, ((bookData['h2h'])['book'])[awayIdx])
            else:
                print(sportID, startTime, homeTeam, bestHome, ((bookData['h2h'])['book'])[homeIdx], awayTeam, bestAway, ((bookData['h2h'])['book'])[awayIdx], 'Draw', bestDraw, ((bookData['h2h'])['book'])[drawIdx])

def main():
    print('*** Welcome to Beat the Bookie ***')
    
    ############ CHOOSE YOUR BOOKS ############
    booksList = []
    selectedBooks = ""
    # loop until we get a valid selection
    while 1:
        state = input("Please enter a two-letter state abbreviation, or type 'MANUAL' to manually select your books: ")
        state = state.upper()
        if state != 'MANUAL':
            # user has provided a two-letter state to fetch the list of available books
            booksList = globals().get(state, "Please enter a valid 2-letter state abbreviation")
            if booksList == "Please enter a valid 2-letter state abbreviation":
                # user did not provide a valid state abbreviation, so print the default text block and retry
                print(booksList)
                continue
            # typing 'ALL_BOOKS' in the state code input will bypass this next step and load in all available books
            if state != 'ALL_BOOKS':
                offshore = input("Would you like to include offshore books? Type 'y' or 'n': ")
                if offshore.lower() == 'y':
                    booksList += OFFSHORE_BOOKS
            for i in range(len(booksList)):
                # create a text block that says which books we are using
                selectedBooks += Books_Print[booksList[i]] + ", "
            # chop off final ', '
            selectedBooks = selectedBooks[0:-2]
        else:
            for i in range(len(Books_Print)):
                # print full numbered list of books to allow users to choose
                print(i+1, Books_Print[i])
            
            manual_books = input("Select which books you would like to load in, separated by commas: ")
            # separate user list from text string into list
            selectedBooks = delimitInput(manual_books, booksList, Books_Print, False)
        
        break

    print("List of books loaded:", selectedBooks)
    time.sleep(1)
    print()

    ############ CHOOSE YOUR GAME MODE ############
    global SELECTED_GAME
    
    print("1 HEDGE BETS - Only display results where you have a guaranteed profit")
    print("2 BEST LINES - Show the most favorable lines for every game")
    print("3 SHOW ALL - Display all possible lines and their best odds")
    print("4 LIVE ONLY - Only show games currently in progress")

    while SELECTED_GAME == 0:
        gameMode = input("Please select a game mode: ")
        if gameMode == '1' or gameMode.upper() == 'HEDGE BETS':
            SELECTED_GAME = 1
        elif gameMode == '2' or gameMode.upper() == 'BEST LINES':
            SELECTED_GAME = 2
        elif gameMode == '3' or gameMode.upper() == 'SHOW ALL':
            SELECTED_GAME = 3
        elif gameMode == '4' or gameMode.upper() == 'LIVE ONLY':
            SELECTED_GAME = 4
        else:
            print("Invalid game mode, try again...")

    time.sleep(1)
    print()

    ############ CHOOSE YOUR SPORTS ############
    activeSports = getActiveSports()
    
    # print the top sports list
    print("TOP SPORTS")
    for sportIdx in range(len(TOP_SPORTS_LIST)):
        print(sportIdx+1, TOP_SPORTS_PRINT[sportIdx])

    sports = input("Select which sports you would like to load in, separated by commas, or type 'SHOW ALL': ")

    if sports == "SHOW ALL":
        # increment to be in the proper place for the next list
        sportIdx += 1
        for j in range(sportIdx, sportIdx+len(OTHER_SPORTS_LIST)):
            print(j+1, ALL_SPORTS_PRINT[j])
        sports = input("Select which sports you would like to load in, separated by commas: ")
    elif sports == "ALL_SPORTS":
        sports = ''
        for i in range(1, len(ALL_SPORTS_LIST)+1):
            sports += str(i) + ','
        # remove final ','
        sports = sports[0:-1]

    sportsList = []
    selectedSports = delimitInput(sports, sportsList, ALL_SPORTS_LIST, True, activeSports)

    print("List of sports loaded:", selectedSports)
    time.sleep(1)
    print()

    regions = 'us'
    if any(i >= 20 for i in booksList): regions += ",us2"
    markets = "h2h,spreads,totals"

    if SELECTED_GAME == HEDGE_BET:
        hedge(booksList, sportsList, regions, markets)
    elif SELECTED_GAME == BEST_LINES:
        bestLines(booksList, sportsList, regions, markets)


if __name__ == "__main__":
    main()