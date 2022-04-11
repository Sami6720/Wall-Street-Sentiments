import time
import pandas as pd
import praw
import pickle
from datetime import datetime, date
from psaw import PushshiftAPI
import string
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

up_ratio = 0.75  # min post upvote ratio
post_ups = 20  # min # upvotes on post
cmt_ups = 2  # min # upvotes on comment
top_n_stocks = 5  # number of most mentioned stocks to consider
posts_perday = 1000 # Number of posts to consider for each day


r = praw.Reddit(
    user_agent="sunflora",
    client_id="fQHJvnTwnElH2AOxXIt4nw",
    client_secret="UW3GeW8iCJCHbly-hYqd7Cgscx72Jw"
)
reddit = PushshiftAPI(r)

# csv file from https://www.nasdaq.com/market-activity/stocks/screener?exchange=nasdaq&letter=0&render=download\
stock_screener = pd.read_csv("nasdaq_screener_1649302163756.csv")
stocks = []
for i in range(stock_screener.shape[0]):
    stocks.append(stock_screener['Symbol'][i])


# blacklist and new_words adapted from https://github.com/jklepatch/eattheblocks/blob/master/screencast/290-wallstreetbets-sentiment-analysis/data.py
# blacklist words that might be confused as stock names
blacklist = {'I', 'ELON', 'WSB', 'THE', 'A', 'ROPE', 'YOLO', 'TOS', 'CEO', 'DD', 'IT', 'OPEN', 'ATH', 'PM', 'IRS', 'FOR','DEC', 'BE', 'IMO', 'ALL', 'RH', 'EV', 'TOS', 'CFO', 'CTO', 'DD', 'BTFD', 'WSB', 'OK', 'PDT', 'RH', 'KYS', 'FD', 'TYS', 'US', 'USA', 'IT', 'ATH', 'RIP', 'BMW', 'GDP', 'OTM', 'ATM', 'ITM', 'IMO', 'LOL', 'AM', 'BE', 'PR', 'PRAY', 'PT', 'FBI', 'SEC', 'GOD', 'NOT', 'POS', 'FOMO', 'TL;DR', 'EDIT', 'STILL', 'WTF', 'RAW', 'PM', 'LMAO', 'LMFAO', 'ROFL', 'EZ', 'RED', 'BEZOS', 'TICK', 'IS', 'PM', 'LPT', 'GOAT', 'FL', 'CA', 'IL', 'MACD', 'HQ', 'OP', 'PS', 'AH', 'TL', 'JAN', 'FEB', 'JUL', 'AUG', 'SEP', 'SEPT', 'OCT', 'NOV', 'FDA', 'IV', 'ER', 'IPO', 'MILF', 'BUT', 'SSN', 'FIFA', 'USD', 'CPU', 'AT', 'GG', 'Mar','ARE','GO',
             'ON','J','VERY','REAL','FAST','ANY','GET','UK','HAS','CAN','IQ'}

# adding words to update the dictionary of SentimentIntensityAnalyzer() based on reddit
new_words = {
    'citron': -4.0,
    'hidenburg': -4.0,
    'moon': 4.0,
    'highs': 2.0,
    'mooning': 4.0,
    'long': 2.0,
    'short': -2.0,
    'call': 4.0,
    'calls': 4.0,
    'put': -4.0,
    'puts': -4.0,
    'break': 2.0,
    'tendie': 2.0,
     'tendies': 2.0,
     'town': 2.0,
     'overvalued': -3.0,
     'undervalued': 3.0,
     'buy': 4.0,
     'sell': -4.0,
     'gone': -1.0,
     'gtfo': -1.7,
     'paper': -1.7,
     'bullish': 3.7,
     'bearish': -3.7,
     'bagholder': -1.7,
     'stonk': 1.9,
     'green': 1.9,
     'money': 1.2,
     'print': 2.2,
     'rocket': 2.2,
     'bull': 2.9,
     'bear': -2.9,
     'pumping': -1.0,
     'sus': -3.0,
     'offering': -2.3,
     'rip': -4.0,
     'downgrade': -3.0,
     'upgrade': 3.0,
     'maintain': 1.0,
     'pump': 1.9,
     'hot': 1.5,
     'drop': -2.5,
     'rebound': 1.5,
     'crack': 2.5,}


# clean up comments
def clean(cmt_string):
    """
    :param cmt_string: sentence string
    :return: string without punctuations
    """
    punctuations = cmt_string.translate(str.maketrans('', '', string.punctuation))  # get rid of punctuations
    return punctuations


# limit = number of posts
def get_posts(start_date, end_date, limit):
    """
    :param start_date: unix time of start epoch
    :param end_date: unix time of ending epoch
    :param limit: number of posts to retrieve
    :return: list of praw submission objects
    """
    # We set by default some useful columns
    posts = list(reddit.search_submissions(
        subreddit='wallstreetbets',
        after=start_date,
        before=end_date,
        limit=limit
    ))
    return posts


def get_picks(start, end, limit):
    """
    :param start: Starting epoch
    :param end: Ending epoch
    :param limit: Number of posts to retrieve
    :return: dictionary: {top n_stocks: list of comments about that stock}
    """

    cmt_list = []  # stores all text
    relevant_comments = []
    stock_count = {}  # stores stock_name:count
    stock_cmts = {}  # stores stock_name: [comments]
    pick_cmts = {}  # stock_cmts for top n stocks

    posts = get_posts(start, end, limit)  # retrieve posts

    for submission in posts:
        if submission.score > post_ups:
            cmt_list.append(clean(submission.title))

            if submission.selftext != "":
                cmt_list.append(clean(submission.selftext))

            submission.comments.replace_more(limit=10)  # Number of more_comment objects to replace
            for comment in submission.comments.list():  # get comments + replies
                if comment.score > cmt_ups:
                    cmt_list.append(clean(comment.body))

    for cmt in cmt_list:
        word_list = cmt.split()
        for word in word_list:
            if word.isupper() and word in stocks and word not in blacklist:
                relevant_comments.append(cmt)

                if word not in stock_count:
                    stock_count[word] = 1
                    stock_cmts[word] = [cmt]

                else:
                    stock_count[word] += 1
                    stock_cmts[word].append(cmt)

    sorted_stock_count = dict(sorted(stock_count.items(), key=lambda item: item[1], reverse=True))
    picks = list(sorted_stock_count.keys())[0:top_n_stocks]

    for st in picks:
        pick_cmts[st] = stock_cmts[st]

    return pick_cmts


def sentiment_score(comment_dict):
    """
    :param comment_dict: dictionary of {stock_name: [list of stock comments]}
    :return: dictionary of {stock_name: dictionary of {sentiment:score}}
    """

    jack = SentimentIntensityAnalyzer()
    jack.lexicon.update(new_words)

    top_picks = list(comment_dict.keys())
    score_dict = dict.fromkeys(top_picks)
    for x in score_dict:  # stock = x
        x_comments = comment_dict[x]  # all relevant comments of stock x
        score_dict[x] = {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0}
        for c in x_comments:
            sentiment_dict = jack.polarity_scores(c)
            for key in sentiment_dict.keys():
                score_dict[x][key] += sentiment_dict[key]

        # need to average each entry in score_dict
        for k in score_dict[x]:
            score_dict[x][k] = score_dict[x][k] / len(x_comments)

    return score_dict


def generate_csv_file():
    """
    Generates csv_file of sentiment scores for posts between start_date and end_date
    """

    # Modify these: Year, Month, Day
    start_date = int(datetime(2022, 2, 1).timestamp())
    end_date = int(datetime(2022, 2, 1).timestamp())

    df_list = []  # List of data frames generated
    df_commentDicts = {}  # Date : comment_dictionary

    starting_time = time.time()
    for i in range(int(start_date), int(end_date)+86400,86400):
        curr_date = datetime.fromtimestamp(i).strftime('%Y-%m-%d')
        print(f'Now working on posts from {curr_date}...')
        comment_dictionary = get_picks(i, i+86400, posts_perday)
        df = pd.DataFrame(sentiment_score(comment_dictionary))
        df.index = ['Bearish', 'Neutral', 'Bullish', 'Total_Compound']
        df = df.T
        df.index.name = 'stock'
        dates = [i for x in range(top_n_stocks)]
        df['Date'] = dates
        df_list.append(df)
        df_commentDicts[i] = comment_dictionary
        diff = time.time() - starting_time
        print(f'{curr_date} completed in {diff} seconds')

    final_df = pd.concat(df_list, axis=0)  # Concatenate all the dataframes for each day
    final_df.reset_index()

    # Save the dataframe as a csv file
    x = datetime.fromtimestamp(start_date).strftime('%Y-%m-%d')
    y = datetime.fromtimestamp(end_date).strftime('%Y-%m-%d')
    final_df.to_csv(f'{x}-{y}.csv')


def daily_csv():
    """
    :return: tuple containing dictionary of comments and DataFrame of sentiment scores;
    """
    today = date.today()
    y = today.year
    m = today.month
    d = today.day

    debut = int(datetime(y, m, d).timestamp()) - 86400
    fin = int(datetime(y, m, d).timestamp())

    comment_dictionary = get_picks(debut, fin, posts_perday)
    df = pd.DataFrame(sentiment_score(comment_dictionary))
    df.index = ['Bearish', 'Neutral', 'Bullish', 'Total_Compound']
    df = df.T
    df.index.name = 'stock'
    dates = [debut for x in range(top_n_stocks)]
    df['Date'] = dates
    df.reset_index()

    # Save the dataframe as a csv file
    # x = datetime.fromtimestamp(start_date).strftime('%Y-%m-%d')
    # y = datetime.fromtimestamp(end_date).strftime('%Y-%m-%d')
    # df.to_csv(f'{str(today)}[1].csv')

    return comment_dictionary, df
