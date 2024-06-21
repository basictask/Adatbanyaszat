import dash
from dash import html

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(
        'Szegénység- és tőke adatbázis',
        style={
            'color': 'blue',
            'fontSize': '40px'
        }
    ),
    html.H2('A Világbank'),
    html.P('Főbb tények:'),
    html.Ul([
        html.Li('Gazdaságok száma: 170'),
        html.Li('Időbeli lefedettség: 1974 - 2019'),
        html.Li('Frissítési gyakoriság: Negyedéves'),
        html.Li('Utolsó frissítés: 2020. március 18.'),
        html.Li([
            'Forrás: ',
            html.A(
                children='https://datacatalog.worldbank.org/dataset/poverty-and-equity-database',
                href='https://datacatalog.worldbank.org/dataset/poverty-and-equity-database'
            )
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
