import streamlit as st
import pandas as pd
import hashlib
import sqlite3
import yfinance as yf
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

# Security
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False
# DB Management
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
    conn.commit()

def login_user(username,password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
    data = c.fetchall()
    return data


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data


st.title("Wall Street Sentiments")
menu = ["Home","Login","SignUp"]
choice = st.sidebar.selectbox("Menu",menu)
if choice == "Home":
    st.subheader("Home")
elif choice == "Login":
    st.subheader("Login Section")
    username = st.sidebar.text_input("User Name")
    password = st.sidebar.text_input("Password",type='password')
    if st.sidebar.checkbox("Login"):
        create_usertable()
        hashed_pswd = make_hashes(password)
        result = login_user(username,check_hashes(password,hashed_pswd))
        if result:
            st.success("Logged In as {}".format(username))
            task = st.selectbox("Task",["View trending stocks"])
            if task == "View trending stocks":
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
            else:
                st.warning("Incorrect Username/Password")
elif choice == "SignUp":
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password",type='password')
    if st.button("Signup"):
        create_usertable()
        add_userdata(new_user,make_hashes(new_password))
        st.success("You have successfully created a valid Account")
        st.info("Go to Login Menu to login")


