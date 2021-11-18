from bs4 import BeautifulSoup
import re
import random
import multiprocessing as mp
import requests
import time 

#from bs4.element import ProcessingInstruction

# get the total of pages in the search 
def getMaxPageNum(searchKeyWords, browser, pageToSearchTerm):
    # Build search link
    url = pageToSearchTerm + searchKeyWords

    browser.get(url)
    browser.implicitly_wait(1)
    # Get maximum page number from returned research result
    soup = BeautifulSoup(browser.page_source, "lxml")
    max_num = int(soup.find('input', {'id':'page-number-input'}).get('max'))
    return max_num

# extraction of the information
def informationExtraction(browser, default_link, db):
    # Extract and build data 
    # Parse html information
    soup = BeautifulSoup(browser.page_source, "lxml")
    # Find sections with desired information
    all_div = soup.find_all('div', {'class':'docsum-content'})

    # Create/empty url_list to store all the new urls
    url_list = []
    
    # Iterate to extract information like author, title, journal, etc
    for row in all_div:
        # Build article's individual link
        link = default_link + row.find('a').get('href')
        url_list.append(link)
    
    print("si llego")
    # Operate multiprocessing
    #multiCore(url_list=url_list, all_div = all_div, browser=browser)
    # Operato one process 
    oneCore(url_list=url_list, all_div = all_div, browser=browser, db = db)

    browser.implicitly_wait(1)

    # Click next buttion to navigate to the next page
    browser.find_element_by_xpath('//*[@title="Navigate to the next page of results."]').click()



def multiCore(url_list, all_div, browser):
    # Multiprocessing
    p = mp.Pool()
    
    for url, row in zip(url_list, all_div):
        p.apply_async(extractWrite, args=(url, row, browser))

    # Close pool
    p.close()
    p.join()

def oneCore(url_list, all_div, browser, db):
    #data_list = list()
    for url, row in zip(url_list, all_div):
        data = extractWrite(url, row, browser, db)
    
        #data_list.append(data)
    """
    for i in data_list:
        print(i)
    """


def extractWrite(url, row, browser, db):
    # Extract information and write into MongoDB
    abstract, keywords = singlePageExtract(url, browser)
    # Extract title, author, date and other information
    title = row.find('a').get_text().strip()
    author = row.find('span', {'class':'docsum-authors full-authors'}).get_text().strip() 
    date_raw = row.find('span', {'class':'docsum-journal-citation full-journal-citation'}).get_text() 
    # Use regular expression to get time information
    date = re.findall(r'\d{4}[\s\w{3}\s\d+]*', date_raw)[0]
    # Build data to be loaded into MongoDB
    data = {
        'url': url,
        'title': title,
        'author': author,
        'date': date,
        'abstract': abstract,
        'keywords': keywords
    }
    # Check if already existed
    if db.med_nlp.find_one({'url': url}) != None:
        print(data, 'already exists.')
    else:
        # Insert data into MongoDB's Pubmed database's med_nlp collections
        db.med_nlp.insert_one(data)  


def singlePageExtract(url, browser):
    # Get the abstract and paper keywords
    
    print(url)
    # Set waiting time to avoid high traffic
    browser.implicitly_wait(random.randint(2, 3))
    
    # Get target page information
    try:
        tempo_html = requests.get(url,  headers = requestHeader(url))
        time.sleep(1)
        tempo_soup = BeautifulSoup(tempo_html.text, 'lxml')
    except: 
        print("NO se obtuvo respuesta")
    
    # Find and collect the abstract
    try:
        abstract = tempo_soup.find('div', {'class':'abstract-content selected'}).find('p').get_text().strip()
        
    except:
        abstract = "Abstract unavailable"
    
    # Collect article' keywords
    try:
        keywordsEle = tempo_soup.find('div', {'id':'mesh-terms'}).find('ul').find_all('button')
        keywordsList = []
        for element in keywordsEle:
            keywordsList.append(element.get_text().strip())
        keywords = "; ".join(keywordsList) 
    except:
        keywords = 'KEYWORDS_NA'
    
    return abstract, keywords

UserAgent = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]


def requestHeader(url):
    # Build request headers
    headers = {
            'User-Agent':random.choice(UserAgent),
            'Referer': url,
            'Connection':'keep-alive',
            
            }
    return headers

#'Host':'www.ncbi.nlm.nih.gov'