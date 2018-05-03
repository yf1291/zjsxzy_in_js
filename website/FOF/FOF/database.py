# encoding: utf-8
import pyodbc
import pandas as pd

import const

def DataFrame_JY(query):
    conn = pyodbc.connect(const.JY_DB_PARAM)
    df = pd.read_sql_query(query, con=conn)
    return df