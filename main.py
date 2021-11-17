from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re
import random
import pandas as pd
from pymongo import MongoClient

# website to scrape 
default_link = 'https://www.ncbi.nlm.nih.gov'

# Start web browser
browser = webdriver.Chrome(executable_path='E:\prueba\chromedriver')

"""
# Start MongoDB
MONGO_HOST= 'mongodb://localhost:27017/'
client = MongoClient(MONGO_HOST)

# Create or load Pubmed database
db = client.Pubmed
"""

# keywords to search
searchKeyWords = "diltiazem"

#max_number = getMaxPageNum(browser=browser)

# look over all the pages
count = 1

while count < 2:
    print(count)
    informationExtraction(browser=browser)
    count += 1

print("finish")