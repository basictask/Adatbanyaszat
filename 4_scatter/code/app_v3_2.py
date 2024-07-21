import os
import re
import dash
import pandas as pd
from dash import html, dcc
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Output, Input

# Adathalmaz előkészítése
current_dir = os.path.dirname(os.path.abspath(__file__))
poverty_data = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsData.csv'))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)

gini = 'GINI index (World Bank estimate)'
gini_df = poverty[poverty[gini].notna()]

regions = [
    'East Asia & Pacific', 'Europe & Central Asia', 'Fragile and conflict affected situations', 'High income',
    'IDA countries classified as fragile situations', 'IDA total', 'Latin America & Caribbean', 'Low & middle income',
    'Low income', 'Lower middle income', 'Middle East & North Africa', 'Middle income', 'South Asia',
    'Sub-Saharan Africa', 'Upper middle income', 'World'
]

population_df = poverty_data[
    ~poverty_data['Country Name'].isin(regions) & (poverty_data['Indicator Name'] == 'Population, total')
]

income_share_df = poverty.filter(regex='Country Name|^year$|Income share.*?20').dropna()
income_share_df = income_share_df.rename(columns={
    'Income share held by lowest 20%': '1 Income share held by lowest 20%',
    'Income share held by second 20%': '2 Income share held by second 20%',
    'Income share held by third 20%': '3 Income share held by third 20%',
    'Income share held by fourth 20%': '4 Income share held by fourth 20%',
    'Income share held by highest 20%': '5 Income share held by highest 20%'
}).sort_index(axis=1)

income_share_df.columns = [re.sub(r'\d Income share held by ', '', col).title() for col in income_share_df.columns]
income_share_cols = income_share_df.columns[:-2]

perc_pov_cols = poverty.filter(regex='Poverty gap').columns
perc_pov_df = poverty[poverty['is_country']].dropna(subset=perc_pov_cols)
perc_pov_years = sorted(set(perc_pov_df['year']))

cividis0 = px.colors.sequential.Cividis[0]


def make_empty_fig():
    fig = go.Figure()
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'
    return fig


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div([
    dbc.Col([
        html.H1('Szegénység és Egyenlőség Adatbázis'),
        html.H2('A Világbank'),

    ], style={'textAlign': 'center'}),
    html.Br(),
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            dcc.Dropdown(
                id='year_dropdown',
                value='2010',
                options=[{'label': year, 'value': str(year)} for year in range(1974, 2019)]
            ),
            dcc.Graph(id='population_chart'),
        ], lg=10)
    ]),
    html.Br(),
    html.H2('Gini Index - Világbank Adatok', style={'textAlign': 'center'}),
    html.Br(),
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            dbc.Label('Év'),
            dcc.Dropdown(
                id='gini_year_dropdown',
                placeholder='Válasszon egy évet',
                options=[{'label': year, 'value': year} for year in gini_df['year'].drop_duplicates().sort_values()]
            ),
            html.Br(),
            dcc.Graph(
                id='gini_year_barchart',
                figure=make_empty_fig()
            )
        ], md=12, lg=5),
        dbc.Col([
            dbc.Label('Országok'),
            dcc.Dropdown(
                id='gini_country_dropdown',
                placeholder='Válasszon egy vagy több országot',
                multi=True,
                options=[{'label': country, 'value': country} for country in gini_df['Country Name'].unique()]
            ),
            html.Br(),
            dcc.Graph(
                id='gini_country_barchart',
                figure=make_empty_fig()
            )
        ], md=12, lg=5),
    ]),
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            html.Br(),
            html.H2('Jövedelem Megoszlás', style={'textAlign': 'center'}),
            html.Br(),
            dbc.Label('Ország'),
            dcc.Dropdown(
                id='income_share_country_dropdown',
                placeholder='Válasszon egy országot',
                options=[{'label': country, 'value': country} for country in income_share_df['Country Name'].unique()]
            ),
            dcc.Graph(
                id='income_share_country_barchart',
                figure=make_empty_fig()
            )
        ], lg=10)

    ]),
    html.Br(),
    html.H2(
        'Szegénységi Rés $1.9, $3.2, és $5.5 (% a lakosságból)',
        style={'textAlign': 'center'}
    ),
    html.Br(),
    html.Br(),
    dbc.Row([
        dbc.Col(lg=2),
        dbc.Col([
            dbc.Label('Válassza ki a szegénységi szintet:'),
            dcc.Slider(
                id='perc_pov_indicator_slider',
                min=0,
                max=2,
                step=1,
                included=False,
                value=0,
                marks={
                    0: {'label': '$1.9', 'style': {'color': cividis0, 'fontWeight': 'bold', 'fontSize': 15}},
                    1: {'label': '$3.2', 'style': {'color': cividis0, 'fontWeight': 'bold', 'fontSize': 15}},
                    2: {'label': '$5.5', 'style': {'color': cividis0, 'fontWeight': 'bold', 'fontSize': 15}},
                }
            ),
        ], lg=2),
        dbc.Col([
            dbc.Label('Válassza ki az évet:'),
            dcc.Slider(
                id='perc_pov_year_slider',
                min=perc_pov_years[0],
                max=perc_pov_years[-1],
                step=1,
                included=False,
                value=2018,
                marks={
                    year: {'label': str(year), 'style': {'color': cividis0, 'fontSize': 14}} for year in
                    perc_pov_years[::5]
                }
            )], lg=5),
    ]),
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            dcc.Graph(
                id='perc_pov_scatter_chart',
                figure=make_empty_fig()
            )
        ], lg=10)
    ]),
    dbc.Tabs([
        dbc.Tab([
            html.Ul([
                html.Br(),
                html.Li('Gazdaságok száma: 170'),
                html.Li('Időbeli lefedettség: 1974 - 2019'),
                html.Li('Frissítési gyakoriság: Negyedéves'),
                html.Li('Utolsó frissítés: 2020. március 18.'),
                html.Li([
                    'Forrás: ',
                    html.A(
                        'https://datacatalog.worldbank.org/dataset/poverty-and-equity-database',
                        href='https://datacatalog.worldbank.org/dataset/poverty-and-equity-database'
                    )
                ])
            ])
        ], label='Kulcsfontosságú tények'),
        dbc.Tab([
            html.Ul([
                html.Br(),
                html.Li('Könyv címe: Interaktív Irányítópultok és Adat Alkalmazások Plotly és Dash segítségével'),
                html.Li([
                    'GitHub repo: ',
                    html.A(
                        'https://github.com/basictask/Adatbanyaszat',
                        href='https://github.com/basictask/Adatbanyaszat',
                    )
                ])
            ])
        ], label='Projekt Információk')
    ]),

], style={'backgroundColor': '#E5ECF6'})


@app.callback(
    Output('population_chart', 'figure'),
    Input('year_dropdown', 'value')
)
def plot_countries_by_population(year):
    fig = go.Figure()
    year_df = population_df[['Country Name', year]].sort_values(year, ascending=False)[:20]
    fig.add_bar(
        x=year_df['Country Name'],
        y=year_df[year]
    )
    fig.layout.title = f'Top twenty countries by population - {year}'
    fig.layout.paper_bgcolor = '#E5ECF6'
    return fig


@app.callback(
    Output('gini_year_barchart', 'figure'),
    Input('gini_year_dropdown', 'value')
)
def plot_gini_year_barchart(year):
    if not year:
        raise PreventUpdate

    df = gini_df[gini_df['year'].eq(year)].sort_values(gini).dropna(subset=[gini])
    n_countries = len(df['Country Name'])
    fig = px.bar(
        df,
        x=gini,
        y='Country Name',
        orientation='h',
        height=200 + (n_countries * 20),
        width=650,
        title=gini + ' ' + str(year)
    )
    fig.layout.paper_bgcolor = '#E5ECF6'
    return fig


@app.callback(Output('gini_country_barchart', 'figure'), Input('gini_country_dropdown', 'value'))
def plot_gini_country_barchart(countries):
    if not countries:
        raise PreventUpdate
    df = gini_df[gini_df['Country Name'].isin(countries)].dropna(subset=[gini])
    fig = px.bar(
        df,
        x='year',
        y=gini,
        height=100 + (250 * len(countries)),
        facet_row='Country Name',
        color='Country Name',
        labels={gini: 'Gini Index'},
        title=''.join([gini, '<br><b>', ', '.join(countries), '</b>'])
    )
    fig.layout.paper_bgcolor = '#E5ECF6'
    return fig


@app.callback(Output('income_share_country_barchart', 'figure'), Input('income_share_country_dropdown', 'value'))
def plot_income_share_barchart(country):
    if country is None:
        raise PreventUpdate
    fig = px.bar(
        income_share_df[income_share_df['Country Name'] == country].dropna(),
        x=income_share_cols,
        y='Year',
        barmode='stack',
        height=600,
        hover_name='Country Name',
        title=f'Income Share Quintiles - {country}',
        orientation='h',
    )
    fig.layout.legend.title = None
    fig.layout.legend.orientation = 'h'
    fig.layout.legend.x = 0.2
    fig.layout.legend.y = -0.15
    fig.layout.xaxis.title = 'Percent of Total Income'
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'
    return fig


@app.callback(
    Output('perc_pov_scatter_chart', 'figure'),
    Input('perc_pov_year_slider', 'value'),
    Input('perc_pov_indicator_slider', 'value')
)
def plot_perc_pov_chart(year, indicator):
    indicator = perc_pov_cols[indicator]
    df = (perc_pov_df[perc_pov_df['year'].eq(year)].dropna(subset=[indicator]).sort_values(indicator))
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


if __name__ == '__main__':
    app.run_server(debug=True)
