# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 17:49:26 2024

@author: starw
"""

import streamlit as st
import time
import numpy as np
from fredapi import Fred

tab1, tab2=st.tabs(["미국채 금리","US Market Index"])

with tab1:
    fred = Fred(api_key='e080d086cd7f24619311c2ca42d60949 ')
    data = fred.get_series('DGS10')
    data=data.iloc[-5000:-1]
    st.line_chart(data)

