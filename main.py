# New Plan: Multi-threaded News Web Scraper
# Used to accumulate mulitiple sources on one topic quickly from a variety of different new sources
# 1) Web Scraping a website

# 2) Multi-Threading to help with performance.
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



options = webdriver.ChromeOptions()
options.add_argument('--headless')


driver = webdriver.Chrome(options=options)
driver.get('https://www.google.ca')
# Set up user interaction to determine search
search_box = driver.find_element(By.NAME, 'q')
search_box.send_keys("Boston Red Sox ")
search_box.send_keys(Keys.RETURN)
driver.implicitly_wait(10)

links = driver.find_elements(By.XPATH, '//div[@id="search"]//a')

for link in links:
    print(link.get_attribute('href'), "\n")
# I think at this point we should look into threading. I would like to have some sort of text component as well. Maybe look and see if we can look for top results or something

driver.quit()