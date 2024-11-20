import streamlit as st
import os
import pandas as pd
from datetime import datetime, time, timedelta
import numpy as np
import plotly.express as px # type: ignore
import plotly.graph_objs as go # type: ignore
from datetime import datetime

main_bases = ['SGN', 'HAN', 'DAD', 'CXR', 'HPH', 'VII', 'VCA', 'PQC']

def clean_dataframe(df):
    """
    Hàm làm sạch DataFrame:
    1. Xóa các cột theo chỉ số (3 và 8).
    2. Xóa các hàng từ chỉ số 0 đến 5.
    3. Reset lại chỉ số.
    4. Sử dụng hàng đầu tiên làm header.
    5. Xóa các hàng có giá trị NaN trong cột 'DATE'.
    6. Xóa 2 dòng cuối cùng.
    7. Xóa chuỗi 'VN-' trong cột 'REG'.
    8. Reset lại chỉ số lần cuối.
    
    Tham số:
        df (pd.DataFrame): DataFrame gốc.
    
    Trả về:
        pd.DataFrame: DataFrame đã được làm sạch.
    """
    # Bước 1: Xóa các cột thứ 3 và thứ 8
    df.drop(df.columns[[3, 8]], axis=1, inplace=True)
    
    # Bước 2: Xóa các hàng từ 0 đến 5
    df = df.drop(df.index[0:6])
    
    # Bước 3: Reset lại chỉ số
    df = df.reset_index(drop=True)
    
    # Bước 4: Lấy hàng đầu tiên làm header
    df.columns = df.iloc[0]
    df = df.drop(df.index[0])
    
    # Bước 5: Loại bỏ các dòng có giá trị NaN trong cột 'DATE'
    df = df.dropna(subset=['DATE'])
    
    # Bước 6: Xóa 2 dòng cuối cùng
    df = df[:-2]
    
    # Bước 7: Xóa chuỗi 'VN-' trong cột 'REG'
    if 'REG' in df.columns:
        df['REG'] = df['REG'].str.replace('VN-', '', regex=False)
    
    # Bước 8: Reset lại chỉ số lần cuối
    df = df.reset_index(drop=True)
    
    return df

def combine_flights(df):
    """
    Hàm kết hợp các chuyến bay theo nhóm `REG` và `AC`:
    1. Ghép hai chuyến bay liên tiếp thành một hàng.
    2. Trả về DataFrame mới với các cột theo định dạng yêu cầu.

    Tham số:
        df (pd.DataFrame): DataFrame gốc.

    Trả về:
        pd.DataFrame: DataFrame đã kết hợp theo định dạng mong muốn.
    """
    combined_rows = []

    # Nhóm dữ liệu theo `REG` và `AC`
    grouped = df.groupby(['REG', 'AC'])

    for _, group in grouped:
        # Reset lại index cho mỗi group
        group = group.reset_index(drop=True)

        # Xử lý các chuyến bay theo từng cặp
        for i in range(len(group)):
            # Lấy dữ liệu của chuyến bay hiện tại
            current_flight = [
                group.loc[i, 'DATE'], group.loc[i, 'Route'], 
                group.loc[i, 'FLT'], group.loc[i, 'REG'], 
                group.loc[i, 'AC'], group.loc[i, 'DEP'], 
                group.loc[i, 'ARR'], group.loc[i, 'STD'], 
                group.loc[i, 'STA']
            ]
            
            # Kiểm tra nếu có chuyến bay tiếp theo
            if i + 1 < len(group):
                # Thêm FLT, DEP, ARR, STD, STA của chuyến bay tiếp theo
                current_flight.extend([
                    group.loc[i + 1, 'FLT'], 
                    group.loc[i + 1, 'DEP'], group.loc[i + 1, 'ARR'], 
                    group.loc[i + 1, 'STD'], group.loc[i + 1, 'STA']
                ])
            else:
                # Nếu không có chuyến bay tiếp theo, để trống FLT, DEP, ARR, STD, STA
                current_flight.extend(['', '', '', '', ''])
            
            combined_rows.append(current_flight)

    # Tạo DataFrame kết quả
    result_df = pd.DataFrame(combined_rows, columns=[
        'DATE', 'Route', 'FLT_1', 'REG', 'AC', 
        'DEP_1', 'ARR_1', 'STD_1', 'STA_1', 
        'FLT_2', 'DEP_2', 'ARR_2', 'STD_2', 'STA_2'
    ])
    
    return result_df

# Xú lý dữ liệu của STA và STD
def adjust_sta_std_datetime(df):
    """
    Điều chỉnh thời gian STA dựa trên ngày và so sánh với STD.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.

    Trả về:
        pd.DataFrame: DataFrame đã điều chỉnh thời gian STA.
    """
    # Kết hợp DATE với STA để tạo datetime
    df['STA'] = pd.to_datetime(df['DATE'] + ' ' + df['STA'], format='%d/%m/%y %H:%M', errors='coerce')
    df['STD'] = pd.to_datetime(df['DATE'] + ' ' + df['STD'], format='%d/%m/%y %H:%M', errors='coerce')

    # Nếu STA < STD, điều chỉnh STA thuộc về ngày hôm sau
    df.loc[df['STA'] < df['STD'], 'STA'] += pd.Timedelta(days=1)

    return df


def get_preflight(df, main_bases):
    """
    Hàm lấy dòng đầu tiên của mỗi REG và lọc các chuyến bay có DEP_1 thuộc mainbase.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay.
        main_bases (list): Danh sách các mainbase.

    Trả về:
        pd.DataFrame: DataFrame chứa các chuyến bay đã được lọc.
    """
    # Nhóm theo REG và lấy dòng đầu tiên của mỗi REG
    first_rows = df.groupby('REG').first().reset_index()
    
    # Lọc các chuyến bay có DEP_1 thuộc mainbases
    filtered_df = first_rows[first_rows['DEP_1'].isin(main_bases)]
    
    return filtered_df

##
def visualize_overlap(df):
    """
    Tạo biểu đồ hiển thị khoảng thời gian overlap giữa các chuyến bay.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay với các cột 'REG', 'START', 'END'.

    Trả về:
        None: Hiển thị biểu đồ hoặc thông báo không có overlap.
    """
    # Bước 1: Tạo một DataFrame để lưu trữ thông tin overlap
    overlap_data = []

    # Bước 2: Lặp qua các dòng để kiểm tra overlap
    for i in range(len(df) - 1):
        end_time = pd.to_datetime(df.loc[i, 'END'])
        start_time_next = pd.to_datetime(df.loc[i + 1, 'START'])
        
        # Kiểm tra overlap
        if end_time > start_time_next:
            overlap_duration = end_time - start_time_next
            overlap_data.append({
                'REG': df.loc[i, 'REG'],
                'Overlap Start': start_time_next,
                'Overlap End': end_time,
                'Duration': overlap_duration,
                'START': df.loc[i, 'START'],  # Thêm cột START
                'END': df.loc[i, 'END']       # Thêm cột END
            })

    # Bước 3: Chuyển đổi overlap_data thành DataFrame
    overlap_df = pd.DataFrame(overlap_data)

    # Bước 4: Biểu diễn dữ liệu
    if not overlap_df.empty:
        fig = px.timeline(overlap_df, x_start='Overlap Start', x_end='Overlap End', y='REG',
                          title='Overlap Times Between Flights',
                          labels={'REG': 'REG', 'Overlap Start': 'Start Time', 'Overlap End': 'End Time'})
        fig.update_yaxes(categoryorder='total ascending', showgrid=True)  # Thêm đường kẻ trục y
        fig.update_layout(yaxis_title='REG', xaxis_title='Time')  # Tùy chỉnh tiêu đề trục
        
        # Thêm chú thích cho thời gian bắt đầu và kết thúc
        for i, row in overlap_df.iterrows():
            fig.add_annotation(x=row['START'], y=row['REG'], text=row['START'].strftime('%H:%M'), showarrow=True, ax=-20, ay=0)
            fig.add_annotation(x=row['END'], y=row['REG'], text=row['END'].strftime('%H:%M'), showarrow=True, ax=20, ay=0)

        st.plotly_chart(fig)
    else:
        print("Không có khoảng thời gian overlap nào.")