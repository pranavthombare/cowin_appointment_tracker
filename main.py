import requests
import json
import pandas as pd 
import datetime
from datetime import timedelta
from hashlib import sha256
import streamlit as st
import os

base_url = "https://cdn-api.co-vin.in/api"
browser_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}

def genOTP(number):
    gen_url = f'{base_url}/v2/auth/public/generateOTP'
    response = requests.post(gen_url , data= json.dumps({"mobile": number}))
    details = json.loads(response.content)
    details_df = pd.DataFrame(details.items(), columns=['txnId','code'])
    return details_df

def confirmOTP(otp, txnid):
    auth_url = f'{base_url}/v2/auth/public/confirmOTP'
    response = requests.post(auth_url , data = json.dumps({'otp' : sha256(int(otp).encode('utf-8')).hexdigest(), 'txnId' : txnid}))
    details = json.loads(response.content)
    details_df = pd.DataFrame(details)
    return details_df

def getStates():
    state_url = f'{base_url}/v2/admin/location/states'
    response = requests.get(state_url, headers = browser_header)
    states = json.loads(response.content)
    states_df = pd.DataFrame(states['states'])
    return states_df #returns dataframe

def getDistrict(state_id):
    district_url = f'{base_url}/v2/admin/location/districts/{state_id}'
    response = requests.get(district_url, headers = browser_header)
    districts = json.loads(response.content)
    district_df = pd.DataFrame(districts['districts'])
    return district_df #returns dataframe

def appointmentByPin(pincode,date):
    appointment_url = f'{base_url}/v2/appointment/sessions/public/findByPin'
    response = requests.get(appointment_url, params = {'pincode': pincode, 
                                                    'date': date},
                                            headers = browser_header)

    appointments = json.loads(response.content)
    appointments_df = pd.DataFrame(appointments['sessions'])
    return appointments_df

def appointmentByDistrict(district_id,date):
    appointment_url = f'{base_url}/v2/appointment/sessions/public/findByDistrict'
    response = requests.get(appointment_url, params={'district_id': district_id, 
                                                    'date': date},
                                            headers = browser_header)
    appointments = json.loads(response.content)
    appointments_df = pd.DataFrame(appointments['sessions'])
    return appointments_df

def weeklyAppointmentByPin(pincode,date):
    appointment_url = f'{base_url}/v2/appointment/sessions/public/calendarByPin'
    response = requests.get(appointment_url, params = {'pincode': pincode, 
                                                    'date': date},
                                            headers = browser_header)

    appointments = json.loads(response.content)
    appointments_df = pd.DataFrame(appointments['sessions'])
    return appointments_df

def weeklyAppointmentByDistrict(district_id,date):
    appointment_url = f'{base_url}/v2/appointment/sessions/public/calendarByDistrict'
    response = requests.get(appointment_url, params = {'district_id': district_id, 
                                                    'date': date},
                                            headers = browser_header)
    appointments = json.loads(response.content)
    appointments_df = pd.DataFrame(appointments['sessions'])
    return appointments_df



st.title('CoWIN Appointment Tracker')

st.write("Use the Sidebar to select state, district and the date for which you want to check the availibility of an appointment.")

TODAY = datetime.date.today()
DATE_LIST = [ TODAY + timedelta(days=x)  for x in range(0,7)]

STATES = getStates()

state_name = st.sidebar.selectbox('Select state',STATES['state_name'])
#st.write(f'{state_name} has following districts')

STATE_ID = STATES.loc[STATES['state_name'] == state_name, 'state_id'].item()
DISTRICTS = getDistrict(STATE_ID)

district_name = st.sidebar.selectbox('Select District',DISTRICTS['district_name'])
DISTRICT_ID = DISTRICTS.loc[DISTRICTS['district_name'] == district_name, 'district_id'].item()

DATE = st.sidebar.selectbox('Select date',DATE_LIST).strftime('%d-%m-%Y')


#district_number = input('Enter Disctrict number: ')
#st.write(appointmentByDistrict(DISTRICT_ID,DATE))

#Filters
result = appointmentByDistrict(DISTRICT_ID,DATE)
VACCINE_FILTER = st.sidebar.selectbox("Select vaccine",result['vaccine'].unique() )

#Final result
FINAL = result[(result['vaccine'] == VACCINE_FILTER) & (result['available_capacity'] >= 1)]
#st.write(FINAL)

for row in FINAL.itertuples():
    newline = '\n'
    st.write("______________________________")
    st.write(f"Doses available at {row.name}:") 
    st.write(f"Dose 1 =>{row.available_capacity_dose1} \n\nDose 2=> {row.available_capacity_dose2}")
    st.write(f"Address: {row.address}")
    st.write(f"slots as follows")
    st.write(row.slots)
    st.write(f"Minimum age: {row.min_age_limit} and above")


#st.write(appointmentByPin(, DATE))

