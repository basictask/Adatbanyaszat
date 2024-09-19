import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1(
        'Szegénység és Egyenlőség Adatbázis',
        style={
            'color': 'blue',
            'fontSize': '40px'
        }),
    html.H2('A Világbank'),
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

        ], label='Főbb tények'),
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

if __name__ == '__main__':
    app.run_server(debug=True)
