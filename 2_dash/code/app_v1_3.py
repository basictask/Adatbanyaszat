import dash
from dash import html 
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

app.layout = html.Div([

    html.H1(
        'Szegénység és Egyenlőség Adatbázis',
        style={
            'color': 'blue',
            'fontSize': '40px'
        }
    ),
    html.H2('A Világbank'),
    html.P('Kulcsfontosságú tények:'),
    html.Ul([
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
    ]),
    html.P('external_stylesheets=[dbc.themes.DARKLY]')
])

if __name__ == '__main__':
    app.run_server(debug=True)
