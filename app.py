import streamlit as st
import pandas as pd
import numpy as np


teptin = st.file_uploader('chon file')
st.write("kich thuoc tap tin la",teptin.size) 