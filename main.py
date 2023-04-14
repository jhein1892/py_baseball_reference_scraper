# New Plan: Multi-threaded News Web Scraper
# Used to accumulate mulitiple sources on one topic quickly from a variety of different new sources
# 1) Web Scraping a website

# 2) Multi-Threading to help with performance.
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys



# options = webdriver.ChromeOptions()
# options.add_argument('--headless')


# driver = webdriver.Chrome(options=options)
# driver.get('https://www.google.ca')
# # Set up user interaction to determine search
# search_box = driver.find_element(By.NAME, 'q')
# search_box.send_keys("Boston Red Sox ")
# search_box.send_keys(Keys.RETURN)
# driver.implicitly_wait(10)

# links = driver.find_elements(By.XPATH, '//div[@id="search"]//a')

# for link in links:
#     print(link.get_attribute('href'), "\n")
# # I think at this point we should look into threading. I would like to have some sort of text component as well. Maybe look and see if we can look for top results or something

# driver.quit()

## So I'm going to pivot again, and go with scraping for baseball Data
# I want to print previous stats (not sure if I want to go with season or lifetime averages)'
# I want to print projected stats
# I want to current stats up until now -> Extrapolate on how close projections are to current performance.

import requests
from bs4 import BeautifulSoup, SoupStrainer
payload = {'search': "Justin Turner"}
r = requests.get('https://www.baseball-reference.com/search/search.fcgi', payload)
# print(r.url)
data = r.text

only_relevant_url = SoupStrainer(class_='search-item-url')
only_relevant_players = SoupStrainer(id='players')
soup = BeautifulSoup(data, 'html.parser', parse_only=only_relevant_players)
my_players = soup.find_all(only_relevant_url)

for player in my_players:
    # This gives the relevant url to add to https://www.baseball-reference.com
    print(player.text)



