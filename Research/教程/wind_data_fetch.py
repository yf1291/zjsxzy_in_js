# encoding: utf-8
import cx_Oracle
import pandas as pd

def get_dataframe(query):
    conn = cx_Oracle.connect('js_dev', '123456', 'wind')
    df = pd.read_sql(query, conn)
    return df