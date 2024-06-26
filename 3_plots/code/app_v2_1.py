import os
import dash
import pandas as pd
from dash import html, dcc
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

current_dir = os.path.dirname(os.path.abspath(__file__))  # Aktuális script mappája
poverty_data = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsData.csv'))

regions = [
    'East Asia & Pacific', 'Europe & Central Asia', 'Fragile and conflict affected situations', 'High income',
    'IDA countries classified as fragile situations', 'IDA total', 'Latin America & Caribbean', 'Low & middle income',
    'Low income', 'Lower middle income', 'Middle East & North Africa', 'Middle income', 'South Asia',
    'Sub-Saharan Africa', 'Upper middle income', 'World'
]
population_df = poverty_data[
    ~poverty_data['Country Name'].isin(regions) & (poverty_data['Indicator Name'] == 'Population, total')
]

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
                        href='https://datacatalog.worldbank.org/dataset/poverty-and-equity-database')
                ])
            ])
        ], label='Kulcsfontosságú tények'),
        dbc.Tab([
            html.Ul([
                html.Br(),
                html.Li('Könyv címe: Interaktív Irányítópultok és Adatalkalmazások Plotly és Dash segítségével'),
                html.Li([
                    'GitHub tárhely: ',
                    html.A('https://github.com/basictask/Adatbanyaszat', 'https://github.com/basictask/Adatbanyaszat')
                ])
            ])
        ], label='Projekt Információk')
    ]),
])


def register_callbacks(param_app):
    """
    A register_callbacks() függvény célja, hogy a Dash alkalmazásban regisztrálja a callback függvényeket.
    Ez a függvény általában egy másik modulban van definiálva, és az alkalmazás fő szkriptjében hívják meg,
    hogy a callback-eket elkülönítve tartsák a fő alkalmazás logikájától.
    """
    @param_app.callback(
        Output('report', 'children'),
        Input('country', 'value')
    )
    def display_country_report(country):
        if country is None:
            return ''

        filtered_df = poverty_data[
            (poverty_data['Country Name'] == country) & (poverty_data['Indicator Name'] == 'Population, total')
        ]
        population = filtered_df.loc[:, '2010'].values[0]
        return [html.H3(country), f'{country} lakossága 2010-ben {population:,.0f} fő volt.']

    @param_app.callback(
        Output('population_chart', 'figure'),
        Input('year_dropdown', 'value')
    )
    def plot_countries_by_population(year):
        fig = go.Figure()
        year_df = population_df[['Country Name', year]].sort_values(year, ascending=False)[:20]
        fig.add_bar(x=year_df['Country Name'], y=year_df[year])
        fig.layout.title = f'A húsz legnépesebb ország - {year}'
        return fig


register_callbacks(app)


if __name__ == '__main__':
    app.run_server(debug=True)
