import cx_Oracle
import pandas as pd

def DataFrame_from_wind(query):
    conn = cx_Oracle.connect('js_dev', '123456', 'wind')
    df = pd.read_sql_query(query, con=conn)
    return df