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

search_box = driver.find_element(By.NAME, 'q')
search_box.send_keys("Boston Red Sox")
search_box.send_keys(Keys.RETURN)
driver.implicitly_wait(10)
# title = driver.title


links = driver.find_elements(By.XPATH, '//div[@id="search"]//a')

# print(links)

for link in links:
    print(link.get_attribute('href'), "\n")
#id: res
#class: yuRUbf

# content = driver.find_element(By.TAG_NAME, "button")
# print(title)

driver.quit()