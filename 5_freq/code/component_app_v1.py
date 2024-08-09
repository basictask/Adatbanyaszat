import os
import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update

# Adatkészlet beolvasása
current_dir = os.path.dirname(os.path.abspath(__file__))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)

# Alkalmazás példányosítása
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

# Alkalmazás elrendezése
app.layout = html.Div(
    children=[
        html.Div(id='component_feedback'),
        dbc.Label('Hozza létre a saját legördülő menüjét, soronként:'),
        dcc.Textarea(
            id='component_text',
            cols=40,
            rows=5,
            style={'width': '100%', 'height': 200},
        ),
        dbc.Button('Beállítások mentése', id='component_button'),
        dcc.Dropdown(id='component_dropdown'),
        dcc.Graph(id='component_chart'),
    ],
    style={'padding': '20px'},
)


# Callback függvények definiálása
@app.callback(
    Output('component_dropdown', 'options'),
    Output('component_feedback', 'children'),
    Input('component_button', 'n_clicks'),
    State('component_text', 'value')
)
def set_dropdown_options(n_clicks, options):
    """
    A gomb megnyomására frissíti a legördülő menü opcióit a szövegmezőbe beírt szavak alapján, és megjelenít egy
    sikeres visszajelző üzenetet.
    """
    if not n_clicks:
        return no_update
    text = options.split()
    message = dbc.Alert(
        f"Az opció hozzáadása sikeresen megtörtént: {','.join(text)}",
        color='success',
        dismissable=True
    )
    for country_code in text:
        if country_code not in poverty['Country Code'].to_list():
            message = dbc.Alert(
                f"Érvénytelen országkód: {country_code}",
                color='danger',
                dismissable=True,
            )
            return no_update, message
    options = [{'label': t, 'value': t} for t in text]
    return options, message


@app.callback(
    Output('component_chart', 'figure'),
    Input('component_dropdown', 'value')
)
def create_population_chart(country_code):
    """
    A legördülő menü kiválasztott értéke alapján frissíti a diagramot, amely
    az adott ország népességének változását mutatja be az évek során.
    """
    if not country_code:
        return no_update
    # Adatkészlet szűrése
    df = poverty[poverty['Country Code'] == country_code]
    # Diagram létrehozása
    return px.line(
        df,
        x='year',
        y='Population, total',
        title=f"Population of {country_code}"
    )


if __name__ == '__main__':
    app.run_server(debug=True)
