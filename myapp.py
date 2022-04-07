from asyncio.windows_events import NULL
from msilib.schema import Component
from statistics import mode
import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests
from pandas import json_normalize
import streamlit.components.v1 as components

import base64


from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
from sklearn.metrics import auc, roc_auc_score, plot_roc_curve, confusion_matrix, ConfusionMatrixDisplay, precision_recall_curve, PrecisionRecallDisplay, plot_confusion_matrix, precision_score, recall_score
from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler

from PIL import Image
image = Image.open('bets_guy.jpg')

st.image(image)

st.write("""
# Wall Street Sentiments
""")

st.write("""
### Stocks reddit is feeling good-about today!

| Stock | Name | Opening Price |
| ----------- | ----------- | ----------- |
| HMHC | Houghton Mifflin Harcourt |21.01 |
| TLRY | Tilray, Inc |7.12 |
| AMD | Advanced Micro Devices, Inc |103.92 |

""")

st.write("""
### Don't buy these! At least that's what the redditors think.

| Stock | Company Name | Opening Price |
| ----------- | ----------- |----------- |
| TSLA | Tesla |1052.39 |
| SOFI | SoFi Technologies, Inc |8.28 |

""")


st.write("""
### Historical price of the hot-5
""")
df_merged  = pd.read_csv('2022-04-07.csv')
STOCKS = list(df_merged['stock'].unique())


#define the ticker symbol
tickerSymbol = st.selectbox(
     'Select the stock you would like to see',
    tuple(STOCKS))#Note that we converted it to tupple.

#get data on this ticker
tickerData = yf.Ticker(tickerSymbol)
#get the historical prices for this ticker
tickerDf = tickerData.history(period='1d', start='2017-3-31', end='2022-3-31')
# Open	High	Low	Close	Volume	Dividends	Stock Splits

st.line_chart(tickerDf.Open)


#Comments
st.write("""
### Comments for the stock
""")

tickerSymbol2 = st.selectbox(
     'Select stocks for comments from reddit!',
    tuple(STOCKS))

with open('daily_comments.pkl', 'rb') as f:
    stock_comments = pickle.load(f)


st.write(stock_comments[tickerSymbol2])


# def img_to_bytes(img_path):
#     img_bytes = Path(img_path).read_bytes()
#     encoded = base64.b64encode(img_bytes).decode()
#     return encoded
# header_html = "<img src='data:image/png;base64,{}' class='img-fluid'>".format(
#     img_to_bytes("bg.jpeg")
# )
# st.markdown(
#     header_html, unsafe_allow_html=True,
# )
# st.markdown(
#     """
#     <style>
#     .reportview-container {
#         background: url("https://i.redd.it/kjvdc916y6051.jpg")
#     }
# `   {
#         background: url("https://i.redd.it/kjvdc916y6051.jpg")
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )