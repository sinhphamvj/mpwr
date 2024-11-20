import streamlit as st
import os
import pandas as pd
from datetime import datetime, time, timedelta
import numpy as np
import plotly.express as px # type: ignore
import plotly.graph_objs as go # type: ignore
from datetime import datetime

main_bases = ['SGN', 'HAN', 'DAD', 'CXR', 'HPH', 'VII', 'VCA', 'PQC']

# Get all REG preflight at mainbase

def get_all_REG_preflight(df, main_bases):
    """
    Hàm lấy dòng đầu tiên của mỗi REG và lọc các chuyến bay có DEP_1 thuộc mainbase.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.
        main_bases (list): Danh sách các mainbase.

    Trả về:
        pd.DataFrame: DataFrame chứa các chuyến bay đã được lọc.
    Example:
    - Mặc định trả về DataFrame chứa các chuyến bay có DEP_1 thuộc mainbase
    - Lọc SGN, or HAN...
        df_day1_preflight_sgn = get_all_REG_preflight(df_day1_combined,['SGN'])
    """
    # Nhóm theo REG và lấy dòng đầu tiên của mỗi REG
    first_rows = df.groupby('REG').first().reset_index()
    
    # Lọc các chuyến bay có DEP_1 thuộc mainbases
    filtered_df = first_rows[first_rows['DEP_1'].isin(main_bases)]

    # Sort STD_1 acsending
    filtered_df = filtered_df.sort_values(by='STD_1')
    # Reset index
    filtered_df.reset_index(drop=True, inplace=True)
    
    return filtered_df

def calculate_preflight_crs_times(df):
    """
    Tính toán thời gian START và END cho CRS.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.

    Trả về:
        pd.DataFrame: DataFrame chứa các cột START, END và STA.
    """

    # Đảm bảo cột DATE là định dạng datetime
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')

    # Kiểm tra xem có giá trị NaT nào trong cột DATE không
    if df['DATE'].isnull().any():
        print("Có ngày không hợp lệ trong cột DATE.")

    # Tính toán thời gian START (trước 90 phút)
    df['START'] = df['STD_1'] - pd.Timedelta(minutes=90)

    # Tính toán thời gian END = STD + 10 phút)
    df['END'] = df['STD_1'] + pd.Timedelta(minutes=10)

    # Thêm cột STA với giá trị 4:30
    df['START_SHIFT'] = pd.to_datetime(df['DATE'].dt.date.astype(str) + ' 04:30')

    return df

# vẽ biểu đồ 
