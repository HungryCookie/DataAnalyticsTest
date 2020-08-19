import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import plotly.express as px
import pandas as pd
import re
from datetime import datetime as dt

from maindash import app
from utils import normalize_text
from config import data_path


df = pd.read_csv(data_path)
df['YEAR'] = df.apply(lambda row: str(row['MONTH'])[:4], axis=1)
df['MONTH_N'] = df.apply(lambda row: str(row['MONTH'])[-2:], axis=1).astype(int)
df['CLAIM_SPECIALTY'] = df['CLAIM_SPECIALTY'].apply(lambda x: normalize_text(str(x)))


def make_layout():
    return html.Div([
        html.H2(children='Data'),
        # ============ Table Related Parts =============
        # DatePicker, Slider, Btns ...
        html.Div([
            html.Div([
                html.Label('Enter the date range of transactions:'),
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=dt(2018, 1, 5),
                    max_date_allowed=dt(2020, 9, 19),
                    initial_visible_month=dt(2018, 8, 5),
                    end_date=None,
                    start_date=None
                ),
                html.Div(id='output-container-date-picker-range'),
                html.Button(
                    'Clear date',
                    id='clear_date_btn'
                )
            ],
                className='three columns'
            ),

            html.Div([
                html.Label('Select Range of Transaction Amount'),
                dcc.RangeSlider(
                    id='my-range-slider',
                    min=df['PAID_AMOUNT'].min(),
                    max=df['PAID_AMOUNT'].max(),
                    step=(df['PAID_AMOUNT'].max() - df['PAID_AMOUNT'].min()) // 10000,
                    value=[df['PAID_AMOUNT'].min(), df['PAID_AMOUNT'].max()]
                ),
                html.Div(id='output-container-range-slider'),
                html.Button(
                    'Clear range',
                    id='clear_range_btn'
                )
            ], className='five columns')
        ],
            className='row',
            style={'width': '90%', 'padding-left': '5%', 'padding-right': '5%'}
        ),

        # ============ Table Itself =============
        html.Br(),
        html.Div([
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                filter_action="native",
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="multi",
                row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action="native",
                page_current=0,
                page_size=10
            ),
            html.Div(id='datatable-interactivity-container'),
        ], style={'width': '90%', 'padding-left': '5%', 'padding-right': '5%'}),



        # ============ Data Visualization (Plots, Charts, Bars..) =============
        html.Br(),
        html.H2('Visualization'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='graph_service_category',
                    figure=px.pie(df, values='PAID_AMOUNT', names='SERVICE_CATEGORY',
                                  title='Paid amount per service category'),
                )
            ], className='six columns'),

            html.Div([
                dcc.Graph(
                    id='graph_payers',
                    figure=px.pie(df, values='PAID_AMOUNT', names='PAYER', title='Paid amount per payer'),
                )
            ], className='six columns'),
        ],
            className='row',
            style={'width': '90%', 'padding-left': '5%', 'padding-right': '5%'}
        ),

        html.Div([
            html.H5('Payers\' monthly payment'),
            dcc.Graph(
                id='bar-graph',
                figure=px.bar(df,
                              x='MONTH_N', y='PAID_AMOUNT', color='PAYER', title='Paid amount per month',
                              facet_col='YEAR')
            )
        ], style={'width': '90%', 'padding-left': '5%', 'padding-right': '5%'}),

        html.Br(),
        html.Div([
            html.H5('Yearly payment stats for Payers'),
            html.Br(),

            dcc.Graph(
                id='payer-year-graph',
                figure=px.bar(df, x='PAYER', y='PAID_AMOUNT', color='YEAR',
                       barmode='group', height=500, title='Years\' comparison')
            ),
            html.Br(),

            html.Div([
                html.H5('Yearly payment for each Payer'),
                html.Label('Select the payer'),
                dcc.Dropdown(
                    id='graph-dropdown',
                    options=[{'label': x, 'value': x} for x in df['PAYER'].unique()],
                    searchable=False,
                    value=df['PAYER'].unique()[0],
                ),
                dcc.Graph(
                    id='solo-payer-year-graph',
                    figure=px.bar(df.loc[df['PAYER'] == df['PAYER'].unique()[0]], x='YEAR', y='PAID_AMOUNT',
                                  color='YEAR')
                ),
            ], style={'width': '70%', 'padding-left': '15%', 'padding-right': '15%'}),


        ], style={'width': '90%', 'padding-left': '5%', 'padding-right': '5%'})

    ])


@app.callback(
    dash.dependencies.Output('solo-payer-year-graph', 'figure'),
    [dash.dependencies.Input('graph-dropdown', 'value')])
def update_output(value):
    return px.bar(df.loc[df['PAYER'] == value], x='YEAR', y='PAID_AMOUNT')


@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('my-range-slider', 'value')])
def update_output(value):
    ''' output the selected PAID_AMOUNT range '''

    if value is not None:
        return 'Range: from {} to {}'.format(value[0], value[1])
    return 'Range: None'


@app.callback(
    [dash.dependencies.Output('my-date-picker-range', 'start_date'),
    dash.dependencies.Output('my-date-picker-range', 'end_date')],
    [dash.dependencies.Input('clear_date_btn', 'n_clicks')],
    [dash.dependencies.State('my-date-picker-range', 'start_date'),
     dash.dependencies.State('my-date-picker-range', 'end_date')])
def clear_date(n_clicks, current_selected_start_date, current_selected_end_date):
    ''' clears the date when button is clicked '''

    if (n_clicks is not None) and (n_clicks > 0):
        return [None, None]
    else:
        return current_selected_start_date, current_selected_end_date


@app.callback(
    dash.dependencies.Output('my-range-slider', 'value'),
    [dash.dependencies.Input('clear_range_btn', 'n_clicks')],
    [dash.dependencies.State('my-range-slider', 'value')])
def clear_date(n_clicks, range_value):
    ''' clears the paid_amount range '''

    if (n_clicks is not None) and (n_clicks > 0):
        return [df['PAID_AMOUNT'].min(), df['PAID_AMOUNT'].max()]
    else:
        return range_value


@app.callback(
    dash.dependencies.Output('table', 'data'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date'),
     dash.dependencies.Input('my-range-slider', 'value')])
def update_table(start_date, end_date, slider_value):
    ''' updates table after certain input '''

    range = list()
    result = df.copy()

    # Check if the date range was selected
    if start_date is not None:
        start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        range.append(str(start_date.year) + str(start_date.month).zfill(2))

        if end_date is not None:
            end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
            range.append(str(end_date.year) + str(end_date.month).zfill(2))
        else:
            range.append(-1)

        if range[1] is not None and int(range[1]) > 0:
            result = result.loc[(result['MONTH'].astype(int) >= int(range[0])) & (result['MONTH'].astype(int) <= int(range[1]))]
        else:
            result = result.loc[result['MONTH'] == int(range[0])]


    # Check slider, if there was paid_amount slicing
    if slider_value is not None:
        start_amount, end_amount = slider_value
        result = result.loc[(result['PAID_AMOUNT'] >= start_amount) & (result['PAID_AMOUNT'] <= end_amount)]

    return result.to_dict('records')
