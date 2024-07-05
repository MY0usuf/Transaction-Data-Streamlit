from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
import time
import datetime

transaction_dir = os.getcwd() + '\\transaction_csv'
download_dir = os.getcwd() + '\\download_csv'

PATH = os.getcwd() + '\\chromedriver.exe'

def extract_date(filename):
    date_str = filename.split("_")[1].split(".")[0]
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

def scroll_down(driver):
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight/4);')

def scroll_up(driver):
    driver.execute_script('window.scrollTo(0, 0);')

def download_transaction_v2(download_dir, transaction_dir):
    base_url = 'https://dubailand.gov.ae/en/open-data/real-estate-data/#/'
    files = os.listdir(transaction_dir)
    dates = [extract_date(filename) for filename in files if "data_" in filename]

    driver = initialize_browser(base_url, download_dir)

    all_dates = set(
        (datetime.date(2024, 1, 1) + datetime.timedelta(days=x))
        for x in range((datetime.date.today() - datetime.date(2024, 1, 1)).days + 1)
        if (datetime.date(2024, 1, 1) + datetime.timedelta(days=x)).weekday() not in {5, 6}
    )

    missing_dates = sorted(all_dates - set(dates))
    print(len(missing_dates))
    for date in missing_dates:
        if date.weekday() < 5:
            try:
                driver.refresh()
                scroll_up(driver)
                process_date(driver, base_url, date)
            except Exception as e:
                print(f"Error processing {date.strftime('%Y-%m-%d')}: {e}")
                driver.refresh()
                time.sleep(5)  # Give some time for the page to reload
                scroll_up(driver)

    driver.quit()

def process_date(driver, base_url, date):
    day = date.strftime('%d')
    month_int = int(date.strftime('%m'))
    month = str(month_int - 1)
    year = date.strftime('%Y')
    print(date.strftime("%Y-%m-%d"))

    action = ActionChains(driver)

    transaction_element = driver.find_element(By.LINK_TEXT, 'Transactions')
    driver.implicitly_wait(1)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, 'Transactions')))
    transaction_element.click()
    time.sleep(4)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "transaction_pFromDate")))
    from_date_picker = driver.find_element(By.ID, 'transaction_pFromDate')
    from_date_picker.click()
    from_date_picker.clear()
    from_date_picker.send_keys(f'{day}/{month_int}/{year}')
    driver.implicitly_wait(1)

    select_month_from_date = Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]'))
    select_month_from_date.select_by_value(month)

    to_date_picker = driver.find_element(By.ID, 'transaction_pToDate')
    to_date_picker.click()
    to_date_picker.clear()
    to_date_picker.send_keys(f'{day}/{month_int}/{year}')
    select_month_to_date = Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]'))
    select_month_to_date.select_by_value(month)
    
    scroll_down(driver)
    search_csv = driver.find_element(By.XPATH, '//*[@id="trxFilter"]/div/div[10]/div/button[1]')
    time.sleep(2)
    search_csv.click()
    time.sleep(10)
    scroll_down(driver)
    time.sleep(2)
    download_csv = driver.find_element(By.XPATH, '//*[@id="transaction"]/div/div/div[1]/div/div/button')
    time.sleep(1)
    download_csv.click()
    
    try:
        WebDriverWait(driver, 60).until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="loading"]/div/div')))
    except TimeoutException:
        print("Loading element did not disappear. Continuing with download.")
    
    scroll_up(driver)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, '//*[@id="transaction"]/div/div/div[1]/div/div/button')))

    time.sleep(4)
    for file in os.listdir('download_csv'):
        if file.endswith('csv'):
            os.rename(os.path.join(download_dir, file), os.path.join(transaction_dir, f'data_{date}.csv'))

    print(f'completed {date.strftime("%Y-%m-%d")}')


def initialize_browser(base_url, download_dir):
    options = Options()
    options.add_experimental_option('prefs', {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "pdfjs.disabled": True
    })
    service = Service(executable_path=PATH)
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(base_url)
    driver.implicitly_wait(0.5)

    return driver

download_transaction_v2(download_dir, transaction_dir)
