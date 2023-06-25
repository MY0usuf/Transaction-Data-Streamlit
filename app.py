import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
from streamlit_autorefresh import st_autorefresh
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

st_autorefresh(interval = 10 * 60 * 60 * 1000, key="dataframerefresh")

def extract_date(filename):
    date_str = filename.split("_")[1].split(".")[0]
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

def scroll_down(driver):
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight/4);')

base_url = 'https://dubailand.gov.ae/en/open-data/real-estate-data/#/'
chrome_file = '\\chromedriver.exe'
download_dir = os.getcwd() + '\\download_csv'
transaction_dir = os.getcwd() + '\\transaction_csv'

PATH = os.getcwd() + chrome_file

def download_transaction(base_url,download_dir,date):
    # Initialising the chrome webdriver by adding certain options 
    options = Options()
    options.add_experimental_option('prefs',  {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "pdfjs.disabled": True
    }
    )

    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications") # to open the window fully
    #service = Service(executable_path=PATH)
    #service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options) # Initialising the driver by giving out the PATH to chromedriver.exe
    
    # Getting Todays Date and Month to use while filling out the form
    day = date.strftime('%d')
    month_int = int(date.strftime('%m'))
    month = str(month_int - 1)
    year = date.strftime('%Y')
    #month = str(month - 1)


    driver.get(base_url)
    driver.implicitly_wait(0.5) 

    action = ActionChains(driver)

    # Switching the navbar to Transactions tab if necessary
    transaction_element = driver.find_element(By.LINK_TEXT, 'Transactions')
    driver.implicitly_wait(1)
    transaction_element.click()
    time.sleep(4)

    # Finding the from date form element to enter the date
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "transaction_pFromDate")))
    from_date_picker = driver.find_element(By.ID, 'transaction_pFromDate')
    from_date_picker.click()
    from_date_picker.clear()
    from_date_picker.send_keys(f'{day}/{month_int}/{year}')
    driver.implicitly_wait(1)

    # Selecting the current month in the datepicker UI
    select_month_from_date = Select(driver.find_element(By.XPATH, '//*[@id="ui-datepicker-div"]/div/div/select[1]'))
    select_month_from_date.select_by_value(month)

    # Finding the to date form element to enter the date
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
    time.sleep(4)
    driver.quit()
    for file in os.listdir('download_csv'):
        if file.endswith('csv'):
            os.rename(os.path.join(download_dir,file),os.path.join(transaction_dir,f'data_{date}.csv'))

# Adjust the width of the main content area
st.markdown(
    """
    <style>
    .reportview-container .main .block-container{
        max-width: 12000px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
@st.cache_data
def get_data():

    files = os.listdir('transaction_csv')
    dates = [extract_date(filename) for filename in files if "data_" in filename]

    all_dates = set(   # Using this we can search upto 2 weeks from todays date
    datetime.date.today() - datetime.timedelta(weeks=2) + datetime.timedelta(days=x)
    for x in range((datetime.date.today() - (datetime.date.today() - datetime.timedelta(weeks=2))).days)
    )
    
    missing_dates = sorted(all_dates - set(dates))
    print(len(missing_dates))
    for date in missing_dates:
        if date.weekday() < 5:
            print(date.strftime("%Y-%m-%d"))
            download_transaction(base_url,download_dir,date)
    
    time.sleep(5)
    values = {'Transaction Number':0,'Transaction Date':0,'Property ID':0,'Transaction Type':'None','Transaction sub type':'None','Registration type':'None','Is Free Hold?':'None','Usage':'None','Area':'None','Property Type':'None','Property Sub Type':'None','Amount':0,'Transaction Size (sq.m)':0,'Property Size (sq.m)':0,'Property Size (sq.ft)':0,'Amount (sq.m)':0,'Amount (sq.ft)':0,'Room(s)':'None','Parking':'None','No. of Buyer':0,'No. of Seller':0,'Master Project':'None','Project':'None'}

    empty_list = []

    for filename in os.listdir('transaction_csv'):
        if filename.endswith('.csv'):
            print(filename)
            df = pd.read_csv(os.path.join('transaction_csv/', filename), dtype={'Property ID':int, 'Amount':float, 'Transaction Size (sq.m)':float, 'Property Size (sq.m)':float,'No. of Buyer':int, 'No. of Seller':int, 'Project':str})
            df.fillna(0)
            #df = df.drop(columns=["Nearest Metro", "Nearest Mall", "Nearest Landmark"])
            empty_list.append(df)

    raw_data = pd.concat(empty_list)

    count_row = raw_data.shape[0]

    size_list = [0]*count_row

    raw_data.insert(14,"Property Size (sq.ft)",size_list,True)
    raw_data.insert(15,"Amount (sq.m)",size_list,True)
    raw_data.insert(16,"Amount (sq.ft)",size_list,True)

    raw_data["Property Size (sq.ft)"] = raw_data["Property Size (sq.m)"] * 10.7639104167
    raw_data["Amount (sq.m)"] = raw_data["Amount"] / raw_data["Property Size (sq.m)"]
    raw_data["Amount (sq.ft)"] = raw_data["Amount"] / raw_data["Property Size (sq.ft)"]

    raw_data['Transaction Date'] = pd.to_datetime(raw_data['Transaction Date']).dt.normalize()

    raw_data.sort_values(by='Transaction Date', inplace = True)

    raw_data.fillna(value = values, inplace = True)

    raw_data['Area'] = raw_data['Area'].str.title()
    raw_data['Project'] = raw_data['Project'].str.title()
    raw_data = raw_data
    raw_data = raw_data.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
    return raw_data.drop(columns=["Nearest Metro", "Nearest Mall", "Nearest Landmark"])
    return pd.read_parquet('raw_transaction_data.parquet')

df = get_data().reset_index(drop=True)

'# Transaction Data'
# Forms can be declared using the 'with' syntax

# Getting the Unique Projects,Areas from the data and adding them onto a single variable
projects_areas = ['All'] + sorted(df['Project'].unique().tolist()) + sorted(df['Area'].unique().tolist())
projects = df['Project'].unique()
areas = df['Area'].unique()
# Getting the Unique Rooms from the data
rooms = ['All'] + df['Room(s)'].unique().tolist()
# Getting the Unique Property Sub type from the data
property_sub_type_list = ['All'] + df['Property Sub Type'].unique().tolist()
# setting the property type into a list
property_type_list = ['All','Land','Unit','Building']
# setting the transaction type into a list
transaction_type_list = ['All','Sales','Mortgage','Gifts']
# setting the Registration type into a list
registration_type_list = ['All','Ready','Off-Plan']
# setting the usage type into a list
usage_type_list = ['All','Residential','Commercial','Other']
# setting the default date to 01 january 2001
start_date_default = datetime.datetime(2001, 1, 1).date()

with st.form(key='my_form', clear_on_submit = True):
    project_area = st.selectbox('Search Project or Area', projects_areas, key='project+area')
    with st.expander("Filter"):
        c1, c2, c3, c4 = st.columns(4)
        b1, b2, b3 = st.columns(3)
        with c1:
            start_date = st.date_input('Start Date', key='start_date',value = start_date_default, max_value=datetime.datetime.today())
        with c2:
            property_type = st.selectbox('Property Type', property_type_list, key='property_type')
        with c3:
            room = st.selectbox('Room(s)', rooms, key='room')
        with c4:
            usage_type = st.selectbox('Usage',usage_type_list, key='usage_type')
        with b1:
            transaction_type = st.selectbox('Transaction Type', transaction_type_list, key='Transaction_type')
        with b2:
            property_sub_type = st.selectbox('Property Sub Type', property_sub_type_list, key='property_sub_type')
        with b3:
            registration_type = st.selectbox('Registration type', registration_type_list, key = 'registration type')
    
    submit_button = st.form_submit_button(label='Submit')


    if submit_button:

        mask = pd.Series(np.ones(df.shape[0], dtype=bool))

        if project_area != 'All':
            if project_area in projects:
                mask &= df['Project'] == project_area
            elif project_area in areas:
                mask &= df['Area'] == project_area

        if property_type != 'All':
            mask &= df['Property Type'] == property_type

        if room != 'All':
            mask &= df['Room(s)'] == room

        if usage_type != 'All':
            mask &= df['Usage'] == usage_type

        if transaction_type != 'All':
            mask &= df['Transaction Type'] == transaction_type

        if property_sub_type != 'All':
            mask &= df['Property Sub Type'] == property_sub_type

        if registration_type != 'All':
            mask &= df['Registration type'] == registration_type

        if start_date:
            start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
            mask &= df['Transaction Date'] >= start_date


        matching_rows = df[mask].reset_index(drop=True)
        if matching_rows.empty:
            st.warning("No matching data found.")
        else:
            st.dataframe(matching_rows,width=2000, height=None)
