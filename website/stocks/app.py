import dash
import dash_table
import pandas as pd

import const

df = pd.read_excel(const.STOCKS_LIST_FILE, usecols='A:U', converters={'股票代码': str})
# df['总分'] = df['总分'].map('{:,.1f}'.format)
df['总分'] = df['总分'].round(2)
df['收盘价'] = df['收盘价'].round(2)
df['动量'] = (df['动量']*100).round(2)
# df['pe(2020)'] = [x if pd.isna(x) else '{:,.2f}'.format(x) for x in df['pe(2020)']]
# df['pe(2021)'] = [x if pd.isna(x) else '{:,.2f}'.format(x) for x in df['pe(2021)']]
# df['pe(2022)'] = [x if pd.isna(x) else '{:,.2f}'.format(x) for x in df['pe(2022)']]
df['pe(2020)'] = df['pe(2020)'].round(2)
df['pe(2021)'] = df['pe(2021)'].round(2)
df['pe(2022)'] = df['pe(2022)'].round(2)
df['增速(2020)'] = [x if pd.isna(x) else '{:,.0f}%'.format(x*100) for x in df['增速(2020)']]
df['增速(2021)'] = [x if pd.isna(x) else '{:,.0f}%'.format(x*100) for x in df['增速(2021)']]
df['增速(2022)'] = [x if pd.isna(x) else '{:,.0f}%'.format(x*100) for x in df['增速(2022)']]

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
        'font_size': '10px',
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