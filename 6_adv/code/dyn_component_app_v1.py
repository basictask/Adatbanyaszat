import dash
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, no_update, dcc

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
    new_chart = dcc.Graph(figure=px.bar(title=f"Diagram {n_clicks}"))
    children.append(new_chart)
    return children


if __name__ == '__main__':
    app.run_server(debug=True)
