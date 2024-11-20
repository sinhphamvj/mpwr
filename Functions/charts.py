import streamlit as st
import os
import pandas as pd
from datetime import datetime, time, timedelta
import numpy as np
import plotly.express as px # type: ignore
import plotly.graph_objs as go # type: ignore
from datetime import datetime


main_bases = ['SGN', 'HAN', 'DAD', 'CXR', 'HPH', 'VII', 'VCA', 'PQC']

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

##
def visualize_overlap(df):
    """
    Tạo biểu đồ hiển thị khoảng thời gian overlap giữa các chuyến bay.

    Tham số:
        df (pd.DataFrame): DataFrame chứa dữ liệu chuyến bay với các cột 'REG', 'START', 'END'.

    Trả về:
        None: Hiển thị biểu đồ hoặc thông báo không có overlap.
    """
    # Bước 1: Sắp xếp DataFrame theo cột 'START'
    df['START'] = pd.to_datetime(df['START'])  # Đảm bảo cột START là kiểu datetime
    df = df.sort_values(by='START').reset_index(drop=True)  # Sắp xếp theo START và reset index

    # Bước 2: Tạo một DataFrame để lưu trữ thông tin overlap
    overlap_data = []

    # Bước 3: Lặp qua các dòng để kiểm tra overlap
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

    # Bước 4: Chuyển đổi overlap_data thành DataFrame
    overlap_df = pd.DataFrame(overlap_data)

    # Bước 5: Biểu diễn dữ liệu
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


def gantt_chart(df):
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