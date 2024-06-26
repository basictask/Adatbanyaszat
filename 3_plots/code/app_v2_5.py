import dash
from get_data import *
from dash import dcc, html
import plotly.express as px
from app_v2_1 import regions
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash.dependencies import Output, Input

# Háttérszín
BGR_COLOR = '#E5ECF6'
# BGR_COLOR = '#FFFFFF'

# Adatok betöltése
current_dir = os.path.dirname(os.path.abspath(__file__))

gini = 'GINI index (World Bank estimate)'
poverty = get_poverty()
gini_df = poverty[poverty[gini].notna()]

income_share_df = get_income_share_df()
income_share_cols = income_share_df.columns[:-2]

poverty_data = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsData.csv'))
population_df = poverty_data[
    ~poverty_data['Country Name'].isin(regions) & (poverty_data['Indicator Name'] == 'Population, total')
]


def make_empty_fig():
    """
    Egy üres Figure objektumot hoz létre
    """
    fig = go.Figure()
    fig.layout.paper_bgcolor = BGR_COLOR
    fig.layout.plot_bgcolor = BGR_COLOR
    return fig


# Alkalmazás inicializálása
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div([
    html.H1('Szegénység és Egyenlőség Adatbázis'),
    html.H2('A Világbank'),
    html.Br(),
    dcc.Dropdown(
        id='year_dropdown',
        value='2010',
        options=[{'label': year, 'value': str(year)} for year in range(1974, 2019)]
    ),
    dcc.Graph(id='population_chart'),
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
                        href='https://github.com/basictask/Adatbanyaszat'
                    )
                ])
            ])
        ], label='Projekt Információk')
    ]),
], style={'backgroundColor': BGR_COLOR})


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
    fig.layout.paper_bgcolor = BGR_COLOR
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
    fig.layout.paper_bgcolor = BGR_COLOR
    return fig


@app.callback(
    Output('gini_country_barchart', 'figure'),
    Input('gini_country_dropdown', 'value')
)
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
    fig.layout.paper_bgcolor = BGR_COLOR
    return fig


@app.callback(
    Output('income_share_country_barchart', 'figure'),
    Input('income_share_country_dropdown', 'value'),
)
def plot_income_share_barchart(country):  # Új callback függvény regisztrálása
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
    fig.layout.paper_bgcolor = BGR_COLOR
    fig.layout.legend.title = None
    fig.layout.legend.orientation = 'h'
    fig.layout.legend.x = 0.2
    fig.layout.xaxis.title = None
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
