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

    # Tính toán thời gian END (START + 40 phút)
    df['END'] = df['START'] + pd.Timedelta(minutes=40)

    # # Thêm cột STA với giá trị 4:30
    # df['STA'] = pd.to_datetime(df['DATE'].dt.date.astype(str) + ' 04:30')

    return df

# vẽ biểu đồ 

def plot_flight_density(df):
    """
    Vẽ biểu đồ thể hiện mật độ chuyến bay theo thời gian.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu với cột 'START'.
    """
    # Chuyển đổi cột START sang datetime
    df['START'] = pd.to_datetime(df['START'], errors='coerce')

    # Tạo một cột mới để nhóm theo khoảng thời gian (ví dụ: mỗi 30 phút)
    df['Time_Group'] = df['START'].dt.floor('30T')  # Làm tròn xuống đến 30 phút

    # Đếm số lượng chuyến bay trong mỗi khoảng thời gian
    density = df.groupby('Time_Group').size().reset_index(name='Flight_Count')

    # Vẽ biểu đồ
    fig = px.line(density, x='Time_Group', y='Flight_Count', title='Flight Density Over Time',
                  labels={'Time_Group': 'Time', 'Flight_Count': 'Number of Flights'})
    
    fig.update_layout(xaxis=dict(tickformat='%H:%M'), yaxis_title='Number of Flights', xaxis_title='Time')
    
    st.plotly_chart(fig)




def preflight_gantt_chart(df):
    """
    Tạo biểu đồ Gantt cho dữ liệu chuyến bay từ combined_df.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu với các cột 'REG', 'START', 'END'.

    Trả về:
        None: Hiển thị biểu đồ Gantt trong Streamlit.
    """
    # Kiểm tra các cột cần thiết có trong DataFrame
    required_columns = ['REG', 'START', 'END']
    if not all(col in df.columns for col in required_columns):
        st.error("DataFrame must contain 'REG', 'START', and 'END' columns.")
        return

    # Chuyển đổi cột START và END sang datetime
    df['START'] = pd.to_datetime(df['START'], errors='coerce')
    df['END'] = pd.to_datetime(df['END'], errors='coerce')

    # Lọc các chuyến bay có cả START và END
    df_filtered = df.dropna(subset=['START', 'END'])

    # Kiểm tra nếu không có dữ liệu sau khi lọc
    if df_filtered.empty:
        st.warning("Không có dữ liệu hợp lệ để hiển thị.")
        return

    # Tạo biểu đồ Gantt
    total_regs = df_filtered['REG'].nunique()
    fig = px.timeline(df_filtered, x_start='START', x_end='END', y='REG', 
                      title=f'Total REGs: {total_regs}', 
                      labels={'REG': 'REG', 'START': 'Start Time', 'END': 'End Time'})

    fig.update_yaxes(categoryorder='total ascending')

    # Thiết lập khoảng thời gian trục x từ 00:00 đến 24:00
    start_range = df_filtered['START'].min().replace(hour=0, minute=0)
    end_range = (df_filtered['END'].max() + pd.Timedelta(days=1)).replace(hour=0, minute=0)
    fig.update_layout(height=800, xaxis=dict(range=[start_range, end_range], tickformat='%H:%M'))

    # Thêm số lượng REGs vào trục y
    fig.update_yaxes(title_text=f'REG (Total: {total_regs})',showgrid = True)

    # Thêm chú thích cho thời gian bắt đầu và kết thúc
    for i, row in df_filtered.iterrows():
        fig.add_annotation(x=row['START'], y=row['REG'], text=row['START'].strftime('%H:%M'), showarrow=True, ax=-20, ay=0)
        fig.add_annotation(x=row['END'], y=row['REG'], text=row['END'].strftime('%H:%M'), showarrow=True, ax=20, ay=0)

    # Hiển thị biểu đồ trong Streamlit
    st.plotly_chart(fig)