import streamlit as st
import pandas as pd
import numpy as np
from Functions.flightplan_process import *

st.title('My first app')
df = pd.read_excel('/Users/dongthan/github/mpwr/7NOV.xlsx')
# Dataframe 
df1 = clean_dataframe(df)

tab1,tab2, tab3,tab4  = st.tabs(['Tab 1', 'Tab 2','Tab 3','Tab 4'])

with tab1:
    st.write('This is tab 1')
    
    st.write(df1)

with tab2:
    st.write('This is tab 2')
    df_combined = combine_flights(df1)
    st.write(df_combined)

with tab3:
    st.write('This is tab 3')
    df_day1_preflight = get_preflight(df_combined, main_bases)
    st.write(df_day1_preflight)

with tab4:
    st.write('This is tab 4')
    df_day1_prefligh_sgn = get_preflight(df_day1_preflight, ['SGN'])
    st.write(df_day1_prefligh_sgn)