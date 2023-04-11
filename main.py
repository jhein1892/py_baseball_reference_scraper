# New Plan: Multi-threaded News Web Scraper
# Used to accumulate mulitiple sources on one topic quickly from a variety of different new sources
# 1) Web Scraping a website

# 2) Multi-Threading to help with performance.
import requests
from bs4 import BeautifulSoup
payload={'q': 'Covid-19', 'section':'all', 'sortOrder':'relevance', 'media':'all'}
r = requests.get('https://www.cbc.ca/search', params=payload)
# print(r.url)
r.status_code

r.headers['content-type']

r.text
soup = BeautifulSoup(r.text, 'html.parser')

print(soup.prettify())