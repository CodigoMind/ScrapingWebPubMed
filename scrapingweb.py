from selenium import webdriver
from pymongo import MongoClient
from scrapingWebDependencies import getMaxPageNum, informationExtraction, singlePageExtract

# parameters: default_link, executable_path, searchKeyWords, pageToSearchTerm

#default_link = 'https://www.ncbi.nlm.nih.gov'
default_link = "https://pubmed.ncbi.nlm.nih.gov"

browser = webdriver.Chrome(executable_path='E:\prueba\chromedriver')

# keywords to search
searchKeyWords = 'diltiazem&adverse&effects'
# page to search the term 
pageToSearchTerm = 'https://www.ncbi.nlm.nih.gov/pubmed/?term='


# Start MongoDB
MONGO_HOST= 'mongodb://localhost:27017/'
client = MongoClient(MONGO_HOST)

# Create or load Pubmed database
db = client.Pubmed


max_number = getMaxPageNum(searchKeyWords, browser=browser, pageToSearchTerm=pageToSearchTerm)

# look over all the pages
count = 1

while count < 200:
    print(count)
    informationExtraction(browser=browser, default_link = default_link, db = db)
    count += 1

