import streamlit as st
import pandas as pd
import numpy as np
# import datetime
from Functions.flightplan_process import *
from Functions.preflight_process import *
from Functions.transit_process import *
# Config pages
st.set_page_config(
    page_title="MPWR APPs",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# st.set_option('deprecation.showPyplotGlobalUse', False)


st.title('MPWR APPs for AMO')
# df = pd.read_excel('/Users/dongthan/github/mpwr/7NOV.xlsx')
# # Dataframe 
# df1 = clean_dataframe(df)

tab1,tab2, tab3,tab4,tab5,tab6  = st.tabs(['Read Flight Plan', 'Flight Plan Cleaned','Preflight','Transit','NightStop','MPWR'])

with tab1:
    st.write('Read flightplan')

    col1, col2 = st.columns(2)

    with col1:
    # Use st.upload to upload a file
        st.write('Please upload a flightplan day 1')
        uploaded_file_day1 = st.file_uploader("Choose a file" ,key = 'uploadfile_1')
        if uploaded_file_day1 is not None:
        # Convert the file to a dataframe
            df_day1 = pd.read_excel(uploaded_file_day1)
            st.write("File uploaded")
       
        else:
            st.write('Please upload a file')

    with col2:
        st.write('Please upload a flightplan day 2')

        uploaded_file_day2 = st.file_uploader("Choose a file" ,key = 'uploadfile_2')
        
        if uploaded_file_day2 is not None:
        # Convert the file to a dataframe
            df_day2 = pd.read_excel(uploaded_file_day2)

            st.write("File uploaded")
        else:
            st.write('Please upload a file')

## Tab2 hiển thị dữ liệu flightplan đã được xử lý ##            
with tab2:

    st.write('Flight Plan Cleaned')

    col1, col2 = st.columns(2)

    with col1:
        st.write('Flight Plan Day 1')
        
        with st.expander('Click to see the flight data day 1'):
   
            df_day1 = clean_dataframe(df_day1)
        # Xứ lý dữ liệu STA và STD 
            df_day1 = adjust_sta_std_datetime(df_day1)
            st.write(df_day1)
        # Combine flights = chuyển dòng chẵn concat với dòng lẻ
        with st.expander('Click to see the combined flight data day 1'):
            st.write("Dữ liệu nối dòng")
            df_day1_combined = combine_flights(df_day1)
            
            st.write(df_day1_combined)

    with col2:
        st.write('Flight Plan Day 2')
        with st.expander('Click to see the flight data day 2'):
            df_day2 = clean_dataframe(df_day2)
            # Xứ lý dữ liệu STA và STD 
            df_day2 = adjust_sta_std_datetime(df_day2)
            st.write(df_day2)
        # Combine flights = chuyển dòng chẵn concat với dòng lẻ
        with st.expander('Click to see the combined flight data day 2'):
            df_day2_combined = combine_flights(df_day2)
            st.write(df_day2_combined)
with tab3:
    st.write('Preflight')

    with st.expander('Get all Preflight in SGN' ):
        df_day1_preflight_sgn = get_all_REG_preflight(df_day1_combined,['SGN'])
        st.write(df_day1_preflight_sgn)

    # Chuẩn hoá giờ START _ END của CRS những chuyến preflight
    with st.expander('CRS START - END Preflight in SGN' ):
        # Apply hàm tính Start và End time
        df_day1_preflight_sgn_START_END = calculate_preflight_crs_times(df_day1_preflight_sgn)

        # Drop the specified columns
        columns_to_drop = ['Route', 'FLT_1', 'AC', 'DEP_1', 'ARR_1','ARR_2', 'STA_1', 'FLT_2', 'DEP_2', 'STD_2', 'STA_2']
        df_day1_preflight_sgn_START_END = df_day1_preflight_sgn_START_END.drop(columns=columns_to_drop, errors='ignore')
        # Rename the column STD_1 to STD
        df_day1_preflight_sgn_START_END = df_day1_preflight_sgn_START_END.rename(columns={'STD_1': 'STD'})
        # Reorder the columns as specified
        new_column_order = ['REG', 'DATE', 'STD', 'START', 'END']
        df_day1_preflight_sgn_START_END = df_day1_preflight_sgn_START_END[new_column_order]

        # Display the modified DataFrame
        st.write(df_day1_preflight_sgn_START_END)
 
    with st.expander('Vẽ sơ đồ biểu diễn chuyến bay đầu ngày ở SGN' ):
        st.write('Vẽ sơ đồ biểu diễn mật độ các chuyến bay đầu ngày')
        fig_preflight = plot_flight_density(df_day1_preflight_sgn_START_END)

    with st.expander("Vẽ các chuyến overlap"):
        ## Vẽ Biểu đồ biểu diễn overlap
        visualize_overlap(df_day1_preflight_sgn_START_END)
    with st.expander('Gant chart preflught'):
        st.write('Gantchart')
        preflight_gantt_chart(df_day1_preflight_sgn_START_END)
# ----
with tab4:
    st.write('Transit')

    with st.expander("Get all transit flight in SGN"):
        df_d1_transit_sgn = filter_transit_flights_at_sgn(df_day1_combined)
        st.write(df_d1_transit_sgn)

    # Chuẩn hoá giờ START _ END của CRS những chuyến transit in SGN
    with st.expander('CRS START - END Trasit in SGN' ):
        # Apply hàm tính Start và End time
        df_d1_transit_sgn_START_END = calculate_crs_transit_times(df_d1_transit_sgn)
        
        st.write(df_d1_transit_sgn_START_END)
with tab5:
    st.write('Nightstop')
