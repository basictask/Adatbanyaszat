import os
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

current_dir = os.path.dirname(os.path.abspath(__file__))  # Aktuális script mappája
poverty_data = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsData.csv'))

app.layout = html.Div([
    html.H1('Szegénység és Egyenlőség Adatbázis'),
    html.H2('A Világbank'),
    dcc.Dropdown(
        id='country',
        options=[
            {'label': country, 'value': country} for country in poverty_data['Country Name'].unique()
        ]
    ),
    html.Br(),
    html.Div(id='report'),
    html.Br(),
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
                        'https://datacatalog.worldbank.org/dataset/poverty-and-equity-database'
                    )
                ])
            ])
        ], label='Kulcsfontosságú tények'),
        dbc.Tab([
            html.Ul([
                html.Br(),
                html.Li([
                    'GitHub repo: ',
                    html.A(
                        'https://github.com/basictask/Adatbanyaszat',
                        'https://github.com/basictask/Adatbanyaszat'
                    )
                ])
            ])
        ], label='Projekt információk')
    ]),
])


@app.callback(
    Output('report', 'children'),
    Input('country', 'value')
)
def display_country_report(country):
    if country is None:
        return ''

    filtered_df = poverty_data[
        (poverty_data['Country Name'] == country) &
        (poverty_data['Indicator Name'] == 'Population, total')
    ]
    population = filtered_df.loc[:, '2010'].values[0]

    return html.H3(country), f'{country} lakossága 2010-ben {population:,.0f} volt.'


if __name__ == '__main__':
    app.run_server(debug=True)
