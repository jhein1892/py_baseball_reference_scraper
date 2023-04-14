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

# Track Time for each Thread
def _timing_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} Elapsed Time: {round(end_time - start_time)} seconds")
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
    # In here I"m going to get and format player career stats
    print('Player Career')

@_timing_decorator
def get_season():
    # In here I"m going to get and format player season stats
    print('Player Season')


print(player_url)
# Create Threads
projection_thread = threading.Thread(target=get_projections)
career_thread = threading.Thread(target=get_career)
season_thread = threading.Thread(target=get_season)

projection_thread.start()
career_thread.start()
season_thread.start()