import os
import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, no_update, dcc, MATCH

# Adatkészlet betöltése
current_dir = os.path.dirname(os.path.abspath(__file__))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)

# Alkalmazás inicializálása
app = dash.Dash(__name__)

# Alkalmazás elrendezése
app.layout = html.Div([
    dbc.Button("Diagram hozzáadása", id='dyn_component_button'),
    html.Div(id='dyn_component_output', children=[]),
])


# Callback függvények
@app.callback(
    Output('dyn_component_output', 'children'),
    Input('dyn_component_button', 'n_clicks'),
    State('dyn_component_output', 'children')
)
def add_new_chart(n_clicks, children):
    if not n_clicks:
        return no_update
    # Új diagram létrehozása
    new_chart = dcc.Graph(
        id={'type': 'chart', 'index': n_clicks},
        figure=px.bar(title=f"Diagram {n_clicks}")
    )
    # Legördülő lista opciók létrehozása
    countries = poverty[poverty['is_country']]['Country Name'].drop_duplicates().sort_values()
    # Legördülő lista létrehozása
    new_dropdown = dcc.Dropdown(
        id={'type': 'dropdown', 'index': n_clicks},
        options=[{'label': c, 'value': c} for c in countries],
        placeholder='Ország kiválasztása'
    )
    # Új Div a komponensekkel
    children.append(
        html.Div([
            html.Br(),
            html.Hr(),
            html.Br(),
            new_chart,
            new_dropdown,
        ])
    )
    return children


@app.callback(
    Output({'type': 'chart', 'index': MATCH}, 'figure'),
    Input({'type': 'dropdown', 'index': MATCH}, 'value'),
)
def create_population_chart(country):
    if not country:
        return no_update
    # Adatkészlet szűrése
    df = poverty[poverty['Country Name'] == country]
    # Diagram létrehozása
    fig = px.line(
        df,
        x='year',
        y='Population, total',
        title=f'{country} ország népessége'
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
