import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
import threading

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

def _format_stats(raw_stats):
    stat_obj = {}
    for stat in raw_stats.find_all('td'):
        data_stat = stat.get('data-stat')
        value = stat.text
        stat_obj[data_stat] = stat_obj.get(data_stat, value)    
    return stat_obj

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
def format_stats():
    #Will probably need to format stats
    print('Formatting Stats')


@_timing_decorator
def get_projections():
    # In here I'm going to get and format my player projections
    print('Player projections')

@_timing_decorator
def get_career():
    career_request = requests.get(player_url)
    data = career_request.text
    stats_table = SoupStrainer(id='batting_standard')
    career_soup = BeautifulSoup(data, 'html.parser', parse_only=stats_table).find('tfoot')

    for row in career_soup.find_all('tr'):
        if row.find('th').find('a'): 
            stats = _format_stats(row)
            player_stats['career'] = player_stats.get('career', stats)
            break
            

@_timing_decorator
def get_season():
    # In here I"m going to get and format player season stats
    print('Player Season')


print(player_url)
# Create Threads

# This can get condensed into a loop
projection_thread = threading.Thread(target=get_projections)
career_thread = threading.Thread(target=get_career)
season_thread = threading.Thread(target=get_season)

projection_thread.start()
career_thread.start()
season_thread.start()

threads = [projection_thread, career_thread, season_thread]

for thread in threads:
    thread.join()


print(f"Players Stats: {player_stats}")