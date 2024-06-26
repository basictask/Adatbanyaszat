import os
import dash
import app_v2_1  # Alkalmazás előző verziói
import app_v2_2
import pandas as pd
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc

# Adathalmaz betöltése
current_dir = os.path.dirname(os.path.abspath(__file__))
poverty_data = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsData.csv'))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)

gini = 'GINI index (World Bank estimate)'

population_df = poverty_data[
    ~poverty_data['Country Name'].isin(app_v2_1.regions) & (poverty_data['Indicator Name'] == 'Population, total')
]

# Alkalmazás inicializálása
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1('Szegénység és Egyenlőség Adatbázis'),
    html.H2('A Világbank'),
    dcc.Dropdown(
        id='country',
        options=[{'label': country, 'value': country} for country in poverty_data['Country Name'].unique()]
    ),
    html.Br(),
    html.Div(id='report'),
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
        dbc.Col([
            dcc.Dropdown(
                id='gini_year_dropdown',
                options=[{'label': year, 'value': year} for year in poverty['year'].unique()]
            ),
            html.Br(),
            dcc.Graph(id='gini_year_barchart')
        ]),
        dbc.Col([
            dcc.Dropdown(
                id='gini_country_dropdown',
                options=[{'label': country, 'value': country} for country in poverty['Country Name'].unique()]
            ),
            html.Br(),
            dcc.Graph(id='gini_country_barchart')
        ]),
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
        ], label='Projekt Információ')
    ]),
])


# Callback függvények regisztrálása
app_v2_1.register_callbacks(app)
app_v2_2.register_callbacks(app)


if __name__ == '__main__':
    app.run_server(debug=True)
