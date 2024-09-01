import dash
from dash import html, dcc, Output, Input

# Alkalmazás példányosítása
app = dash.Dash(__name__)

# Elrendezés komponensek
app.layout = html.Div([
    dcc.Location(id='location', refresh=False),
    html.Div(id='location_output'),
])

# Callback függvények
@app.callback(
    Output('location_output', 'children'),
    Input('location', 'href'),
)
def display_href(href):
    return f'Webcím: {href}'


if __name__ == '__main__':
    app.run_server(debug=True)
