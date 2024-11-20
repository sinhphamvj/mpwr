import streamlit as st
import os
import pandas as pd
from datetime import datetime, time, timedelta
import numpy as np
import plotly.express as px # type: ignore
import plotly.graph_objs as go # type: ignore
from datetime import datetime

main_bases = ['SGN', 'HAN', 'DAD', 'CXR', 'HPH', 'VII', 'VCA', 'PQC']

# 
def filter_transit_flights_at_sgn(df):
    """
    Hàm lọc những chuyến bay transit ở SGN.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.

    Trả về:
        pd.DataFrame: DataFrame chứa các chuyến bay transit ở SGN.
    """
    # Lọc các chuyến bay có ARR_1 = 'SGN' và DEP_2 = 'SGN'
    transit_flights = df[(df['ARR_1'] == 'SGN') & (df['DEP_2'] == 'SGN')]
    
    # Nhóm REG sau đó sắp xếp lại chỉ số STA_1 tăng dần
    
    transit_flights = transit_flights.sort_values('STA_1')

    # Reset index
    transit_flights = transit_flights.reset_index(drop=True)

    return transit_flights

def calculate_crs_transit_times(df):
    """
    Tính toán thời gian START và END cho CRS.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.

    Trả về:
        pd.DataFrame: DataFrame chứa các cột START và END.
    """

    # Tính toán thời gian START (trước 15 phút)
    df['START'] = df['STA_1'] - pd.Timedelta(minutes=15)

    # Tính toán thời gian END = STD + 10 phút
    df['END'] = df['STD_2'] + pd.Timedelta(minutes=10)

    return df