import os
import dash
import warnings
import pandas as pd
from dash import dcc
from dash import html
import plotly.express as px
from dash import Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

warnings.filterwarnings("ignore")

# Adatkészlet beolvasása
current_dir = os.path.dirname(os.path.abspath(__file__))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)
perc_pov_cols = poverty.filter(regex='Poverty gap').columns
perc_pov_df = poverty[poverty['is_country']].dropna(subset=perc_pov_cols)
perc_pov_years = sorted(set(perc_pov_df['year']))

# Alkalmazás színtémája
cividis0 = px.colors.sequential.Cividis[0]

# Alkalmazás példányosítása
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div([
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            html.Br(),
            dbc.Label('Select poverty level:'),
            dcc.Slider(
                id='perc_pov_indicator_slider',
                min=0,
                max=2,
                step=1,
                included=False,
                value=0,
                marks={
                    0: {'label': '$1.9', 'style': {'color': cividis0, 'fontWeight': 'bold'}},
                    1: {'label': '$3.2', 'style': {'color': cividis0, 'fontWeight': 'bold'}},
                    2: {'label': '$5.5', 'style': {'color': cividis0, 'fontWeight': 'bold'}}
                }
            ),
        ], lg=2),
        dbc.Col([
            html.Br(),
            dbc.Label('Select year:'),
            dcc.Slider(
                id='perc_pov_year_slider',
                min=perc_pov_years[0],
                max=perc_pov_years[-1],
                step=1,
                included=False,
                value=2018,
                marks={year: {'label': str(year), 'style': {'color': cividis0}} for year in perc_pov_years[::5]}
            ),
        ], lg=5),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='perc_pov_scatter_chart')
        ])
    ])

], style={'backgroundColor': '#E5ECF6'})


@app.callback(
    Output('perc_pov_scatter_chart', 'figure'),
    Input('perc_pov_year_slider', 'value'),
    Input('perc_pov_indicator_slider', 'value')
)
def plot_perc_pov_chart(year, indicator):
    indicator = perc_pov_cols[indicator]
    df = perc_pov_df[perc_pov_df['year'].eq(year)].dropna(subset=[indicator]).sort_values(indicator)

    if df.empty:
        raise PreventUpdate

    fig = px.scatter(
        df,
        x=indicator,
        y='Country Name',
        color='Population, total',
        size=[30] * len(df),
        size_max=15,
        hover_name='Country Name',
        height=250 + (20 * len(df)),
        color_continuous_scale='cividis',
        title=indicator + '<b>: ' + f'{year}' + '</b>'
    )
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.xaxis.ticksuffix = '%'
    return fig


app.run_server(debug=True, port=8051)
