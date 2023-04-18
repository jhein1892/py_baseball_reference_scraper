import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
import threading
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tabulate import tabulate

def findStats(name):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-css')
    driver = webdriver.Chrome(options=options) # Still make sure that your chrome driver is in PATH or in this folder if it isn't
# Turn this into user input
    try:
        payload = {'search': f"{name}"}
        search_request = requests.get('https://www.baseball-reference.com/search/search.fcgi', payload)
        data = search_request.text
        url = search_request.url
        parsed_url = urlparse(url)
        url_path = parsed_url.path
        player_url = ''
        if '/players' in url_path:
            player_url = url
        else:
            only_relevant_url = SoupStrainer(class_='search-item-url')
            only_relevant_players = SoupStrainer(id='players')
            soup = BeautifulSoup(data, 'html.parser', parse_only=only_relevant_players)
            my_players = soup.find_all(only_relevant_url)

            # update this to work with multiple players
            # for player in my_players:
            player_url = my_players[0].text

            # Create next search's URL
            baseURL = 'https://www.baseball-reference.com'
            player_url = baseURL + player_url
    except IndexError:
        print("Ooopsy, this isn't a player!")
        return


    print(player_url)

    # # # Track Time for each Thread
    def _timing_decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"{func.__name__} Elapsed Time: {round((end_time - start_time), 3)} seconds")
            return result
        return wrapper

    @_timing_decorator
    def _find_position():
        position_request = requests.get(player_url)
        data = position_request.text
        only_meta = SoupStrainer(id='meta')
        soup = BeautifulSoup(data,'html.parser', parse_only=only_meta).find_all('div')
        for div in soup:
            my_tags = div.find_all('p')
            for element in my_tags:
                if 'Position' in element.text:
                    if 'Pitcher' in element.text:
                        return "P"
                    else:
                        return "B"
            
    player_position = _find_position()
    position_mapping = {'B': 'batting', 'P' :'pitching'}
    player_stats = {}
    career_keys = []
    season_keys = []
    proj_keys = []

    @_timing_decorator
    def _format_stats(raw_stats, list):
        keys_mapping = {'career': career_keys, 'season': season_keys, 'proj': proj_keys}
        keys_swapping = {
            "B":{
                'batting_avg': 'AVG', 
                'onbase_plus_slugging_plus': 'OPS+', 
                'slugging_perc':'SLUG%', 
                'onbase_perc':'OBP', 
                'onbase_plus_slugging':'OPS',
                'reliability':'rel'
            },
            "P":{
                'strikeouts_per_base_on_balls':"K/BB",
                'earned_run_avg':'ERA',
                'win_loss_perc':'W/L%',
                'strikeouts_per_nine':'K/9',
                'bases_on_balls_per_nine':'BB/9',
                'home_runs_per_nine':'HR/9',
                'hits_per_nine':'H/9',
                'batters_faced':'BF',
                'earned_run_avg_plus': "ERA+",
                'reliability':'rel'
            }
        }
        ignore_keys = ['award_summary', 'pos_season', 'team_ID', 'lg_ID', 'FIP', 'age', ]
        stat_obj = {}
        for stat in raw_stats.find_all('td'):
            data_stat = stat.get('data-stat')
            if data_stat in ignore_keys:
                continue
            if data_stat in keys_swapping[player_position]:
                data_stat = keys_swapping[player_position][data_stat]
                
            keys_mapping[list].append(data_stat)
            value = stat.text
            stat_obj[data_stat] = stat_obj.get(data_stat, value)    
        return stat_obj

    # This one is being a problem
    @_timing_decorator
    def get_projections():
        driver.get(player_url)
        driver.implicitly_wait(10)
        content = driver.find_element(By.ID, f'{position_mapping[player_position]}_proj') # This is going to need to be specified depending on whether a pitcher or not
        # content = SoupStrainer(id=f'{position_mapping[player_position]}_proj')
        html_string = content.get_attribute('outerHTML')
        driver.quit()

        soup = BeautifulSoup(html_string, 'html.parser')
        stat_section = soup.find('tbody')

        for row in stat_section.find_all('tr'):
            if row.find('a',{'title':'Marcels Projections'}):
                stats = _format_stats(row, 'proj')
                player_stats['proj'] = player_stats.get('proj', stats)
                break

            player_stats['proj'] = player_stats.get('proj', [])

    @_timing_decorator
    def get_career():
        career_request = requests.get(player_url)
        data = career_request.text
        stats_table = SoupStrainer(id=f'{position_mapping[player_position]}_standard') # Will need to be specified depending on whether it not player is a pitcher
        career_soup = BeautifulSoup(data, 'html.parser', parse_only=stats_table).find('tfoot')

        for row in career_soup.find_all('tr'):
            if row.find('th').find('a'): 
                stats = _format_stats(row, 'career')
                player_stats['career'] = player_stats.get('career', stats) 
                break

            player_stats['career'] = player_stats.get('career', []) 
                
                
    @_timing_decorator
    def get_season():
        career_request = requests.get(player_url)
        data = career_request.text
        stats_table = SoupStrainer(id=f'{position_mapping[player_position]}_standard') # Will need to be specified depending on whether the player is pitcher or batter
        career_soup = BeautifulSoup(data, 'html.parser', parse_only=stats_table).find('tbody')
        # print(career_soup.prettify())

        for row in career_soup.find_all('tr'):
            if row.find('th', {'csk':'2023'}):
                stats = _format_stats(row, 'season')
                player_stats['season'] = player_stats.get('season', stats)
                break
            player_stats['season'] = player_stats.get('season', [])
        # print('Player Season')

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

    keys = [career_keys, season_keys, proj_keys]
    useableKeys = []
    for key in keys:
        if len(key) > 0:
            useableKeys.append(key)
        else:
            continue
    




    print(f"Career: {career_keys}\nSeason: {season_keys}\n Proj: {proj_keys}")

    # common_stats = set(career_keys).intersection(season_keys, proj_keys)
    common_stats = set(career_keys).union(season_keys, proj_keys)
    career_values = ['Career(Avg 162)']
    season_values = ['Season']
    proj_values = ['Projections']

    for key in common_stats:
        career_values.append(player_stats['career'][key] if key in player_stats['career'] else 'NA')
        season_values.append(player_stats['season'][key] if  key in player_stats['season'] else 'NA')
        proj_values.append(player_stats['proj'][key] if key in player_stats['proj'] else 'NA')

    common_stats = list(common_stats)
    common_stats.insert(0, 'Time')
    table = tabulate([common_stats, career_values, season_values, proj_values], headers="firstrow", tablefmt="fancy_grid")

    print(table)
name = ''

while name != 'q':
    print("Enter 'q' to quit application")
    name = input('Please Enter the name of the player you would like to see Stats on: ').strip()
    print(f"you've entered: {name}\nHold on while we gather their stats...\n")
    findStats(name)


print('Thank you for using me!')