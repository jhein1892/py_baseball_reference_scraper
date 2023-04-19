
# Baseball Reference Scraper

This is a Python application that allows you to retrieve baseball stats for a given player. It scrapes data from Baseball Reference website, including career stats, season stats, and projected stats. The application uses multithreading to speed up the scraping process by allowing the program to scrape multiple pages at the same time

The application is built using the following tools and technologies:

- BeautifulSoup: A Python library that makes it easy to scrape data from HTML and XML documents
- Selenium: A tool for automating web browsers, which is used in this application to load and scrape data from web pages
- Tabulate: A Python library that formats data into tables for easy display in the terminal

## Installation and Setup
You can clone the repository to your local machine and navigate to the directory to install the required packages. You will need to have Python installed on your machine.

> Please ensure that chromedriver is either located in this directory after cloning the repository or included in your system's PATH environment variables.

<kbd>git clone https://github.com/[username]/baseball-reference-scraper.git</kbd>

<kbd>cd baseball-reference-scraper</kbd>

<kbd>pip install -r requirements.txt</kbd>

## Usage
Run the following command in your terminal to start the application:

<kbd>python baseball-reference-scraper.py</kbd>

The application will prompt you to enter the name of the player whose stats you want to retrieve. You can type 'q' to exit the application.

The application will then scrape the data from Baseball Reference and output the stats in a table format.