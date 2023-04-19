import requests
from bs4 import BeautifulSoup, SoupStrainer
import time
import threading
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By

from tabulate import tabulate

def findStats(name):
    player_name=''
    position_mapping = {'B': 'batting', 'P' :'pitching'}
    player_stats = {}
    common_stats = []

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-css')
    driver = webdriver.Chrome(options=options) # Still make sure that your chrome driver is in PATH or in this folder if it isn't

    try:
        search_request = requests.get('https://www.baseball-reference.com/search/search.fcgi', {'search': f'{name}'})
        data = search_request.text
        url = search_request.url
        print(url)
        player_url = ''
        if '/players' in urlparse(url).path:
            player_url = url
        else:
            only_relevant_url = SoupStrainer(class_='search-item-url')
            only_relevant_players = SoupStrainer(id='players')
            soup = BeautifulSoup(data, 'html.parser', parse_only=only_relevant_players)
            my_players = soup.find_all(only_relevant_url)
            print(my_players)
            # Create next search's URL
            baseURL = 'https://www.baseball-reference.com'
            player_url = baseURL + my_players[0].text # Run on most relevant player
    except IndexError:
        print(f"Hmm, we can't seem to find player {name}")
        return
    
    # Track Time for each Thread
    def _timing_decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"{func.__name__} Elapsed Time: {round((end_time - start_time), 3)} seconds")
            return result
        return wrapper

    def _find_position():
        global player_name
        position_request = requests.get(player_url)
        data = position_request.text
        only_meta = SoupStrainer(id='meta')
        soup = BeautifulSoup(data,'html.parser', parse_only=only_meta).find_all('div')
        for div in soup:
            player_name = div.find('h1').text
            for element in div.find_all('p'):
                if 'Position' in element.text and 'Pitcher' in element.text:
                    return "P"
                elif 'Position' in element.text and not 'Pitcher' in element.text:
                    return "B"
            
    player_position = _find_position()
    
    def _format_stats(raw_stats, list):
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
            }
        }
        ignore_keys = ['award_summary', 'pos_season', 'team_ID', 'lg_ID', 'fip', 'age', 'reliability', 'BF' ]
        stat_obj = {}
        for stat in raw_stats.find_all('td'):
            data_stat = stat.get('data-stat')
            if data_stat in ignore_keys:
                continue
            if data_stat in keys_swapping[player_position]:
                data_stat = keys_swapping[player_position][data_stat]

            if data_stat not in common_stats:
                common_stats.append(data_stat)    

            value = stat.text
            stat_obj[data_stat] = stat_obj.get(data_stat, value)    
        return stat_obj

    # This one is being a problem
    @_timing_decorator
    def get_projections():
        driver.get(player_url)
        driver.implicitly_wait(10)
        try:
            content = driver.find_element(By.ID, f'{position_mapping[player_position]}_proj') # This is going to need to be specified depending on whether a pitcher or not
            html_string = content.get_attribute('outerHTML')
            soup = BeautifulSoup(html_string, 'html.parser')
            stat_section = soup.find('tbody')

            for row in stat_section.find_all('tr'):
                if row.find('a',{'title':'Marcels Projections'}):
                    stats = _format_stats(row, 'proj')
                    player_stats['proj'] = player_stats.get('proj', stats)
                    break
            else:
                player_stats['proj'] = player_stats.get('proj', {})
        except:
            print("Sorry nothing in Projections")
            player_stats['proj'] = player_stats.get('proj', {})
            return

        driver.quit()

    @_timing_decorator
    def get_standard_stats(stat_duration):
        type_mapping = {"season":{'data_div':'tbody'}, "career" : {'data_div':'tfoot'}}

        try:
            career_request = requests.get(player_url)
            data = career_request.text
            stats_table = SoupStrainer(id=f'{position_mapping[player_position]}_standard')
            stat_soup = BeautifulSoup(data, 'html.parser', parse_only=stats_table).find(type_mapping[stat_duration]['data_div'])
        except:
            print(f'Sorry, Nothing for this players {stat_duration}')
            player_stats[stat_duration] = player_stats.get(stat_duration, {})

        for row in stat_soup.find_all('tr'):
            if row.find('th', {'csk': '2023'}) if stat_duration == 'season' else row.find('th').find('a'):
                stats = _format_stats(row, stat_duration)
                player_stats[stat_duration] = player_stats.get(stat_duration, stats)
                break
        else:
            player_stats[stat_duration] = player_stats.get(stat_duration, {})

    # Create Threads
    threads = []
    for duration in ['proj', 'season', 'career']:
        if duration == 'proj':
            thread = threading.Thread(target=get_projections)
        else:
            thread = threading.Thread(target=get_standard_stats, args=(duration,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

    career_values = ['Career(Avg 162)']
    season_values = ['Season']
    proj_values = ['Projections']

    for key in common_stats:
        career_values.append(player_stats['career'][key] if key in player_stats['career'] else 'NA')
        season_values.append(player_stats['season'][key] if  key in player_stats['season'] else 'NA')
        proj_values.append(player_stats['proj'][key] if key in player_stats['proj'] else 'NA')

    common_stats.insert(0, 'Time')
    table = tabulate([common_stats, career_values, season_values, proj_values], headers="firstrow", tablefmt="fancy_grid")
    
    print(f"\n{name}:\n{table}")

while True:
    print("Enter 'q' to quit application")
    name = input('Please Enter the name of the player you would like to see Stats on: ').strip()
    if name.lower() == 'q':
        break
    print(f"you've entered: {name}\nHold on while we gather their stats...\n")
    findStats(name)


print('Thank you for using me!') # 194