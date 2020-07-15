import dash
import dash_table
import pandas as pd

import const

df = pd.read_excel(const.STOCKS_LIST_FILE, usecols='A:R', converters={'股票代码': str})
df['总分'] = df['总分'].map('{:,.1f}'.format)
df['收盘价'] = df['收盘价'].map('{:,.2f}'.format)
df['eps(ttm)'] = df['eps(ttm)'].map('{:,.2f}'.format)
df['pe(ttm)'] = df['pe(ttm)'].map('{:,.2f}'.format)
df['pb(lyr)'] = df['pb(lyr)'].map('{:,.2f}'.format)
df['ps(ttm)'] = df['ps(ttm)'].map('{:,.2f}'.format)
df['股息率(ttm)'] = df['股息率(ttm)'].map('{:,.2f}%'.format)

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict("rows"),
    sort_action="native",
    sort_mode="multi",
    column_selectable="single",
    selected_columns=[],
    selected_rows=[],
    page_action="native",
    page_current= 0,
    page_size= 20,
    filter_action='native',
    style_cell={
        'font_family': 'Microsoft YaHei',
        'font_size': '12px',
        'text_align': 'center'
    },
    style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in ['Date', 'Region']
    ],
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }
    ],
    style_header={
        'backgroundColor': 'rgb(164, 1, 1)',
        'fontWeight': 'bold',
        'color': 'white'
    }
)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')