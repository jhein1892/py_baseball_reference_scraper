import requests
from bs4 import BeautifulSoup, SoupStrainer
payload = {'search': "Justin Turner"}
r = requests.get('https://www.baseball-reference.com/search/search.fcgi', payload)
data = r.text

only_relevant_url = SoupStrainer(class_='search-item-url')
only_relevant_players = SoupStrainer(id='players')
soup = BeautifulSoup(data, 'html.parser', parse_only=only_relevant_players)
my_players = soup.find_all(only_relevant_url)

for player in my_players:
    # This gives the relevant url to add to https://www.baseball-reference.com
    print(player.text)


# This is where I'm going to start threading. 
# Current Season Stats: 


# Career Stats


# Projections for this season

