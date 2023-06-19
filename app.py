import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


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
    return pd.read_parquet('C:\\Users\\yousu\\Desktop\\Python Projects\\Streamlit App\\raw_transaction_data.parquet')

df = get_data().reset_index(drop=True)

'# Transaction Data'
# Forms can be declared using the 'with' syntax

# Getting the Unique Projects,Areas from the data and adding them onto a single variable
projects_areas = ['All'] + df['Project'].unique().tolist() + df['Area'].unique().tolist()
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
start_date_default = datetime(2001, 1, 1).date()

with st.form(key='my_form', clear_on_submit = True):
    project_area = st.selectbox('Search Project or Area', projects_areas, key='project+area')
    with st.expander("Filter"):
        c1, c2, c3, c4 = st.columns(4)
        b1, b2, b3 = st.columns(3)
        with c1:
            start_date = st.date_input('Start Date', key='start_date',value = start_date_default, max_value=datetime.today())
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
            mask &= df['Project'] == project_area

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
            start_date = datetime.combine(start_date, datetime.min.time())
            mask &= df['Transaction Date'] >= start_date


        matching_rows = df[mask].reset_index(drop=True)
        if matching_rows.empty:
            st.warning("No matching data found.")
        else:
            st.dataframe(matching_rows,width=2000, height=None)

        
