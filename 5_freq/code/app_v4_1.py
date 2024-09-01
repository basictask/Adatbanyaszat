import os
import re
import dash
import warnings
import pandas as pd
import plotly.express as px
from pandas_datareader import wb
import plotly.graph_objects as go
from dash import html, dcc, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Output, Input, State

# FutureWarning kiszűrése
warnings.simplefilter(action='ignore', category=FutureWarning)

# Adathalmazok előkészítése
current_dir = os.path.dirname(os.path.abspath(__file__))
poverty_data = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsData.csv'))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)
series = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsSeries.csv'), low_memory=False)

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

# Országnév és ISO ID lekérdezése a tematikus térképezéshez
countries = wb.get_countries()
countries["capitalCity"] = countries["capitalCity"].replace({"": None})
countries.dropna(subset=["capitalCity"], inplace=True)
countries = countries[["name", "iso3c"]]
countries = countries[countries["name"] != "Kosovo"]
countries = countries.rename(columns={"name": "country"})

indicators = {
    "IT.NET.USER.ZS": "Internetet használók aránya (teljes népesség %)",
    "SG.GEN.PARL.ZS": "A nemzeti parlamentekben a nők által betöltött helyek aránya (%)",
    "EN.ATM.CO2E.KT": "CO2-kibocsátás (kt)",
}

cividis0 = px.colors.sequential.Cividis[0]


# Segédfüggvények
def update_wb_data():
    # Világbanki adatok lekérdezése API-ról
    df = wb.download(indicator=(list(indicators)), country=countries["iso3c"], start=2005, end=2016, errors="warn")
    df = df.reset_index()
    df.year = df.year.astype(int)
    # ISO3 oszlop hozzáadása az eredeti adatkészlethez
    df = pd.merge(df, countries, on="country")
    df = df.rename(columns=indicators)
    return df


def make_empty_fig():
    fig = go.Figure()
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'
    return fig


# Alkalmazás példányosítása
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

# Alkalmazás elrendezése
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
    dbc.Row(
        dbc.Col(
            [
                html.H2(
                    "A Világbank országadatainak összehasonlítása",
                    style={"textAlign": "center"},
                ),
                dcc.Graph(id="choropleth_map", figure={}),
            ],
            width=12,
        )
    ),
    dbc.Row(
        [
            dbc.Col(
                html.Div([
                    html.H4("Adatkészlet kiválasztása:"),
                    dcc.RadioItems(
                        id="radio_indicator",
                        options=[{"label": i, "value": i} for i in indicators.values()],
                        value=list(indicators.values())[0],
                        inputClassName="me-2",
                    )
                ], style={'padding': '20px'}),
                width=4,
            ),
            dbc.Col(
                html.Div([
                    html.H4("Évek tartományának kiválasztása:"),
                    dcc.RangeSlider(
                        id="years_range",
                        min=2005,
                        max=2016,
                        step=1,
                        value=[2005, 2006],
                        marks={x: str(x) for x in range(2005, 2017)},
                    )
                ], style={'padding': '20px'}),
                width=8,
            ),
        ]
    ),
    dbc.Row([
        dbc.Col([
            html.H2(
                'Indikátorok megoszlása gyarkoriság szerint',
                style={"textAlign": "center"},
            ),
            # Hisztogramok hozzáadása az alkalmazáshoz
            dbc.Label('Indikátor kiválasztása:'),
            dcc.Dropdown(
                id='hist_indicator_dropdown',
                placeholder='Indikátor',
                options=[{'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]]
            ),
            html.Div(style={'height': '20px'}),  # Vertikális térköz
            dbc.Label('Évek kiválasztása:'),
            dcc.Dropdown(
                id='hist_multi_year_selector',
                multi=True,
                placeholder='Válasszon egy vagy több évet',
                options=[{'label': year, 'value': year} for year in poverty['year'].drop_duplicates().sort_values()]
            ),
            html.Div(style={'height': '20px'}),
            dbc.Label('Kosarak számának kiválasztása:'),
            dcc.Slider(
                id='hist_bins_slider',
                min=0,
                step=5,
                marks={x: str(x) for x in range(0, 105, 5)}
            ),
            dcc.Graph(id='indicator_year_histogram'),
        ])
    ]),
    html.Div(style={'height': '20px'}),
    dcc.Store(id="storage", storage_type="session", data={}),
    dcc.Interval(id="timer", interval=1000 * 60, n_intervals=0),
    html.Div(style={'height': '20px'}),
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
        ], label='Projekt Információk'),
        dbc.Tab([
            html.Div(
                style={'padding': '20px'},
                children=[
                    html.Div(style={'marginBottom': '20px'}),
                    dcc.Dropdown(
                        id='indicator_dropdown',
                        value='GINI index (World Bank estimate)',
                        options=[{'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]]
                    ),
                    dbc.Row(
                        dbc.Col(
                            [
                                dcc.Markdown(
                                    id='indicator_map_details_md',
                                )
                            ],
                            width=12,
                        )
                    ),
                ]
            )
        ], label='Indikátor információk')
    ]),
], style={'backgroundColor': '#E5ECF6', 'padding': '20px'})


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


@app.callback(
    Output('gini_country_barchart', 'figure'),
    Input('gini_country_dropdown', 'value')
)
def plot_gini_country_barchart(gini_countries):
    if not gini_countries:
        raise PreventUpdate
    df = gini_df[gini_df['Country Name'].isin(gini_countries)].dropna(subset=[gini])
    fig = px.bar(
        df,
        x='year',
        y=gini,
        height=100 + (250 * len(gini_countries)),
        facet_row='Country Name',
        color='Country Name',
        labels={gini: 'Gini Index'},
        title=''.join([gini, '<br><b>', ', '.join(gini_countries), '</b>'])
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


@app.callback(
    Output("storage", "data"),
    Input("timer", "n_intervals")
)
def store_data(_):
    dataframe = update_wb_data()
    return dataframe.to_dict("records")


@app.callback(
    Output("choropleth_map", "figure"),
    Input("years_range", "value"),
    Input("radio_indicator", "value"),
    State("storage", "data"),
)
def update_map(years_chosen, indct_chosen, stored_dataframe):
    dff = pd.DataFrame.from_records(stored_dataframe)
    if len(dff) == 0:
        return no_update
    print(years_chosen)

    if years_chosen[0] != years_chosen[1]:
        dff = dff[dff.year.between(years_chosen[0], years_chosen[1])].copy()
        dff[indct_chosen + '_mean'] = dff.groupby(["iso3c", "country"])[indct_chosen].transform('mean')
        dff = dff.reset_index()

    if years_chosen[0] == years_chosen[1]:
        dff = dff[dff["year"].isin(years_chosen)]

    fig = px.choropleth(
        data_frame=dff,
        locations="iso3c",
        color=indct_chosen,
        scope="world",
        hover_data={"iso3c": False, "country": True},
        labels={
            indicators["SG.GEN.PARL.ZS"]: "Nők aránya",
            indicators["IT.NET.USER.ZS"]: "Internethasználók aránya",
        },
    )
    fig.layout.geo.bgcolor = '#E5ECF6'
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'
    fig.update_layout(
        geo={"projection": {"type": "natural earth"}},
        margin=dict(l=50, r=50, t=50, b=50),
    )
    return fig


@app.callback(
    Output('indicator_year_histogram', 'figure'),
    Input('hist_multi_year_selector', 'value'),
    Input('hist_indicator_dropdown', 'value'),
    Input('hist_bins_slider', 'value')
)
def display_histogram(years, indicator, nbins):
    """
    Frissíti a hisztogram ábrát a kiválasztott évek, indikátor és bins értékek alapján
    """
    if not years or not indicator:
        return make_empty_fig()
    if isinstance(years, int):
        years = [years]
    df = poverty[poverty['year'].isin(years) & poverty['is_country']]  # Adatkészlet szűrése
    fig = px.histogram(  # Hisztogram létrehozása
        df,
        x=indicator,
        color='year',
        facet_col='year',
        height=700,
        nbins=nbins,
    )
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'
    fig.for_each_xaxis(lambda axis: axis.update(title=''))
    fig.add_annotation(
        text=indicator,
        y=-0.12,
        yref='paper'
    )
    return fig


@app.callback(
    Output('indicator_map_details_md', 'children'),
    Input("indicator_dropdown", "value"),
)
def update_indicator_map_details_md(indicator):
    # Adatkészlet beolvasása
    series_df = series[series['Indicator Name'].eq(indicator)]
    if series_df.empty:
        markdown = "Nincs elérhető adat az indikátorról"
    else:
        limitations = series_df['Limitations and exceptions'].fillna('N/A').str.replace('\n\n', '').values[0]
        # Markdown komponens szövegének definiálása
        markdown = f"""
            ---
            ## {series_df['Indicator Name'].values[0]}
            {series_df['Long definition'].values[0]}
            * **Mértékegység:** {series_df['Unit of measure'].fillna('count').values[0]}
            * **Periodicitás:** {series_df['Periodicity'].fillna('N/A').values[0]}
            * **Forrás:** {series_df['Source'].values[0]}
            ### Limitációk és kivételek: 
            {limitations}
        """
    return markdown


if __name__ == '__main__':
    app.run_server(debug=True)
