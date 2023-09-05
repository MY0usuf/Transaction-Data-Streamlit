import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import time
import base64

def extract_date(filename):
    date_str = filename.split("_")[1].split(".")[0]
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

transaction_dir = os.getcwd() + '\\transaction_csv'


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
@st.cache_data(ttl=10800)
def get_data():

    values = {'Transaction Number':0,'Transaction Date':0,'Property ID':0,'Transaction Type':'None','Transaction sub type':'None','Registration type':'None','Is Free Hold?':'None','Usage':'None','Area':'None','Property Type':'None','Property Sub Type':'None','Amount':0,'Transaction Size (sq.m)':0,'Property Size (sq.m)':0,'Property Size (sq.ft)':0,'Amount (sq.m)':0,'Amount (sq.ft)':0,'Room(s)':'None','Parking':'None','No. of Buyer':0,'No. of Seller':0,'Master Project':'None','Project':'None'}

    empty_list = []

    for filename in os.listdir('transaction_csv'):
        if filename.endswith('.csv'):
            print(filename)
            df = pd.read_csv(os.path.join('transaction_csv/', filename), dtype={'Property ID':int,"Property Size (sq.ft)":float ,'Amount':float,"Amount (sq.m)": float, 'Transaction Size (sq.m)':float, 'Property Size (sq.m)':float,'No. of Buyer':int, 'No. of Seller':int, 'Project':str})
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

    raw_data['Transaction Date'] = pd.to_datetime(raw_data['Transaction Date']).dt.date

    raw_data.sort_values(by='Transaction Date', inplace = True)

    raw_data.fillna(value = values, inplace = True)

    raw_data['Area'] = raw_data['Area'].str.title()
    raw_data['Project'] = raw_data['Project'].str.title()
    raw_data = raw_data
    raw_data = raw_data.applymap(lambda x: round(x, 2) if isinstance(x, (int, float)) else x)
    return raw_data.drop(columns=["Nearest Metro", "Nearest Mall", "Nearest Landmark"])


df = get_data().reset_index(drop=True)
st.title('Transaction Data')
#'# Transaction Data'
# Forms can be declared using the 'with' syntax

# Getting the Unique Projects,Areas from the data and adding them onto a single variable
projects_areas = ['All','Sobha Hartland Phase 1','Samana All Projects','Al furjan in area'] + sorted(df['Project'].unique().tolist()) + sorted(df['Area'].unique().tolist())
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
        b1, b2, b3, b4 = st.columns(4)
        with c1:
            start_date = st.date_input('Start Date', key='start_date',value = start_date_default, max_value=datetime.datetime.today())
        with c2:
            end_date = st.date_input('End Date', key='end_date',value = datetime.datetime.today(), max_value=datetime.datetime.today())
        with c3:
            property_type = st.selectbox('Property Type', property_type_list, key='property_type')
        with c4:
            room = st.selectbox('Room(s)', rooms, key='room')
        with b1:
            transaction_type = st.selectbox('Transaction Type', transaction_type_list, key='Transaction_type')
        with b2:
            property_sub_type = st.selectbox('Property Sub Type', property_sub_type_list, key='property_sub_type')
        with b3:
            registration_type = st.selectbox('Registration type', registration_type_list, key = 'registration type')
        with b4:
            usage_type = st.selectbox('Usage',usage_type_list, key='usage_type')
    
    submit_button = st.form_submit_button(label='Submit')


    if submit_button:

        mask = pd.Series(np.ones(df.shape[0], dtype=bool))

        if project_area != 'All':
            if project_area == 'Sobha Hartland Phase 1':
                mask = (df['Project'] == 'Sobha Hartland Waves Opulence')|(df['Project'] == 'Sobha Hartland - The Crest')|(df['Project'] == 'Sobha Creek Vistas Grande')|(df['Project'] == 'Sobha Hartland - Crest Grande')|(df['Project'] == 'Sobha Creek Vistas')|(df['Project'] == 'Sobha Hartland One Park Avenue ')|(df['Project'] == 'Sobha Creek Vistas Reserve')|(df['Project'] == 'Sobha Hartland Greens- Phase I')|(df['Project'] == 'Sobha Hartland Greens Phase Ii')|(df['Project'] == 'Sobha Hartland Greens - Phase Iii')|(df['Project'] == 'Sobha Hartland Waves')|(df['Project'] == 'Sobha Hartland Waves Grande')
                #mask &= df['Project'] == ''
            elif project_area == 'Samana All Projects':
                mask = (df['Project'] == 'Samana Mykonos Signature')|(df['Project'] == 'Samana Mykonos')|(df['Project'] == 'Samana Waves')|(df['Project'] == 'Samana Miami')|(df['Project'] == 'Samana Hills')|(df['Project'] == 'Samana Green')|(df['Project'] == 'Samana Skyros')|(df['Project'] == 'Samana Waves 2')|(df['Project'] == 'Samana Santorini')|(df['Project'] == 'Samana Golf View')|(df['Project'] == 'Samana Park Views')|(df['Project'] == 'Samana Golf Avenue')|(df['Project'] == 'Samana Ivy Gardens')|(df['Project'] == 'Miami By Sd')
            elif project_area == 'Al furjan in area':
                mask &= df['Area'] == 'Al Furjan'
            elif project_area in projects:
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
            #start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
            mask &= df['Transaction Date'] >= start_date
        
        if end_date:
            mask &= df['Transaction Date'] <= end_date


        matching_rows = df[mask].reset_index(drop=True)
        average_amount_sq_ft_method_1 = matching_rows['Amount (sq.ft)'].mean(axis=0)
        average_property_size_sq_ft = matching_rows['Property Size (sq.ft)'].mean(axis=0)
        total_amount = matching_rows['Amount'].sum()
        total_property_size_sq_ft = matching_rows['Property Size (sq.ft)'].sum()
        average_amount_sq_ft_method_2 = total_amount / total_property_size_sq_ft
        project_details = matching_rows['Project'].unique().tolist()
        no_of_rooms = matching_rows['Room(s)'].value_counts(dropna=False)
        no_of_rooms_dictionary = no_of_rooms.to_dict()
        if matching_rows.empty:
            st.warning("No matching data found.")
        else:
            st.subheader('Averages')
            st.markdown(f'**Amount per Sq Ft method 1:-** :green[{average_amount_sq_ft_method_1:,.2f}]')
            st.markdown(f'**Amount per Sq Ft method 2:-** :green[{average_amount_sq_ft_method_2:,.2f}]')
            st.markdown(f'**Property Size per Sq Ft:-** :green[{average_property_size_sq_ft:,.2f}]')
            st.subheader('Totals')
            st.markdown(f'**Amount:-** :green[{total_amount:,.2f}]')
            st.markdown(f'**Property Size (Sq Ft):-** :green[{total_property_size_sq_ft:,.2f}]')
            st.markdown(f'**Projects:-** :green[{project_details}]')
            for k, v in no_of_rooms_dictionary.items():
                st.markdown(f'**No Of {k}:-** :green[{v}]')
            st.dataframe(matching_rows,width=2000, height=None)

            # Download the CSV button
            csv_data = matching_rows.to_csv(index=False)
            b64 = base64.b64encode(csv_data.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="matching_rows.csv">Download the CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
