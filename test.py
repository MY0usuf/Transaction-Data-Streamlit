from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from crawlab import save_item

# create web driver with chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
browser = webdriver.Chrome(options=chrome_options)

# navigate to the news list page
browser.get('https://36kr.com/information/web_news/')

# get article items
items = browser.find_elements(by=By.CSS_SELECTOR, value='.information-flow-list > .information-flow-item')

# iterate through items
for item in items:
    # extract fields
    el_title = item.find_element(by=By.CSS_SELECTOR, value='.article-item-title')
    title = el_title.text
    url = el_title.get_attribute('href')
    topic = item.find_element(by=By.CSS_SELECTOR, value='.kr-flow-bar-motif > a').text
    description = item.find_element(by=By.CSS_SELECTOR, value='.article-item-description').text
    try:
        pic_url = item.find_element(by=By.CSS_SELECTOR, value='.article-item-pic > img').get_attribute('src')
    except:
        pic_url = None

    # save to Crawlab
    save_item({
        'title': title,
        'url': url,
        'topic': topic,
        'description': description,
        'pic_url': pic_url,
    })