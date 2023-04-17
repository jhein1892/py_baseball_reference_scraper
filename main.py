import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
import threading

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tabulate import tabulate

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-css')
driver = webdriver.Chrome(options=options) # Still make sure that your chrome driver is in PATH or in this folder if it isn't

# Turn this into user input
payload = {'search': "Justin Turner"}
search_request = requests.get('https://www.baseball-reference.com/search/search.fcgi', payload)
data = search_request.text

# Finds specific player URL
only_relevant_url = SoupStrainer(class_='search-item-url')
only_relevant_players = SoupStrainer(id='players')
soup = BeautifulSoup(data, 'html.parser', parse_only=only_relevant_players)
my_players = soup.find_all(only_relevant_url)

player_url = ''
# update this to work with multiple players
for player in my_players:
    player_url = player.text
    # This gives the relevant url to add to https://www.baseball-reference.com

# Create next search's URL
baseURL = 'https://www.baseball-reference.com'
player_url = baseURL + player_url

player_stats = {}

career_keys = []

season_keys = []
proj_keys = []

# Track Time for each Thread
def _timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} Elapsed Time: {round((end_time - start_time), 3)} seconds")
        return result
    return wrapper

@_timing_decorator
def _format_stats(raw_stats, list):
    keys_mapping = {'career': career_keys, 'season': season_keys, 'proj': proj_keys}
    # values_mapping = {'career': career_values, 'season': season_values, 'proj': proj_values}

    stat_obj = {}
    for stat in raw_stats.find_all('td'):
        data_stat = stat.get('data-stat')
        keys_mapping[list].append(data_stat)
        value = stat.text
        # values_mapping[list].append(value)
        stat_obj[data_stat] = stat_obj.get(data_stat, value)    
    return stat_obj

# This one is being a problem
@_timing_decorator
def get_projections():
    driver.get(player_url)
    driver.implicitly_wait(10)
    content = driver.find_element(By.ID, 'batting_proj') # This is going to need to be specified depending on whether a pitcher or not
    html_string = content.get_attribute('outerHTML')
    driver.quit()

    soup = BeautifulSoup(html_string, 'html.parser')
    stat_section = soup.find('tbody')

    for row in stat_section.find_all('tr'):
        if row.find('a',{'title':'Marcels Projections'}):
            stats = _format_stats(row, 'proj')
            player_stats['proj'] = player_stats.get('proj', stats)

@_timing_decorator
def get_career():
    career_request = requests.get(player_url)
    data = career_request.text
    stats_table = SoupStrainer(id='batting_standard') # Will need to be specified depending on whether it not player is a pitcher
    career_soup = BeautifulSoup(data, 'html.parser', parse_only=stats_table).find('tfoot')

    for row in career_soup.find_all('tr'):
        if row.find('th').find('a'): 
            stats = _format_stats(row, 'career')
            player_stats['career'] = player_stats.get('career', stats)
            break
            

@_timing_decorator
def get_season():
    career_request = requests.get(player_url)
    data = career_request.text
    stats_table = SoupStrainer(id='batting_standard') # Will need to be specified depending on whether the player is pitcher or batter
    career_soup = BeautifulSoup(data, 'html.parser', parse_only=stats_table).find('tbody')
    # print(career_soup.prettify())

    for row in career_soup.find_all('tr'):
        if row.find('th', {'csk':'2023'}):
            # print('here') 
            stats = _format_stats(row, 'season')
            player_stats['season'] = player_stats.get('season', stats)
            break
    # print('Player Season')

# Create Threads

# This can get condensed into a loop
# projection_thread = threading.Thread(target=get_projections)
career_thread = threading.Thread(target=get_career)
season_thread = threading.Thread(target=get_season)

# projection_thread.start()
career_thread.start()
season_thread.start()

# threads = [projection_thread, career_thread, season_thread]
threads = [career_thread, season_thread]

for thread in threads:
    thread.join()


common_stats = set(career_keys).intersection(season_keys)
career_values = ['Season']
season_values = ['Career']
proj_values = ['Projections']
value_mapping = {'career':career_values, 'season': season_values, 'proj': proj_values}
# print(player_stats)
for key in common_stats:
    career_values.append(player_stats['career'][key])
    season_values.append(player_stats['season'][key])
    # proj_values.append(player_stats['proj'][key])

common_stats = list(common_stats)
common_stats.insert(0, 'Time')
table = tabulate([common_stats, career_values, season_values], headers="firstrow")

print(table)
# For each object in stat_timeframe
# 
# On next iteration, if the key we 
# For each key in object
    # if that key is also in the other two, then we want to keep it.

# {
#   'career': 
#       {'G': '162', 'PA': '600', 'AB': '527', 'R': '76', 'H': '152', '2B': '34', '3B': '1', 'HR': '19', 'RBI': '77', 'SB': '5', 'CS': '1', 'BB': '54', 'SO': '90', 'batting_avg': '.289', 'onbase_perc': '.366', 'slugging_perc': '.465', 'onbase_plus_slugging': '.831', 'onbase_plus_slugging_plus': '125', 'TB': '245', 'GIDP': '14', 'HBP': '13', 'SH': '1', 'SF': '5', 'IBB': '2', 'pos_season': '', 'award_summary': ''}, 

#   'season': 
#       {'age': '38', 'team_ID': 'BOS', 'lg_ID': 'AL', 'G': '15', 'PA': '68', 'AB': '55', 'R': '8', 'H': '14', '2B': '4', '3B': '0', 'HR': '0', 'RBI': '4', 'SB': '1', 'CS': '0', 'BB': '9', 'SO': '8', 'batting_avg': '.255', 'onbase_perc': '.382', 'slugging_perc': '.327', 'onbase_plus_slugging': '.710', 'onbase_plus_slugging_plus': '94', 'TB': '18', 'GIDP': '2', 'HBP': '3', 'SH': '0', 'SF': '1', 'IBB': '0', 'pos_season': '*D/3', 'award_summary': ''}, 

#   'projections': 
#       {'team_ID': 'Proj.', 'age': '38', 'PA': '527', 'AB': '464', 'R': '64', 'H': '123', '2B': '26', '3B': '1', 'HR': '16', 'RBI': '71', 'SB': '4', 'CS': '0', 'BB': '47', 'SO': '93', 'batting_avg': '.265', 'onbase_perc': '.339', 'slugging_perc': '.429', 'onbase_plus_slugging': '.768', 'TB': '199', 'GIDP': '11', 'HBP': '8', 'SH': '0', 'SF': '6', 'IBB': '1', 'reliability': '82%'}
# }




# print(f"Players Stats: {player_stats}")