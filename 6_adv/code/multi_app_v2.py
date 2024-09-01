import dash
from dash import html, dcc, Output, Input

# Alkalmazás példányosítása
app = dash.Dash(__name__)

# Elrendezés komponensek
app.layout = html.Div([
    dcc.Location(
        id='location',
        refresh=False
    ),
    html.A(
        href='/path',
        children='Mappába navigálás'
    ),
    html.Br(),
    dcc.Link(
        href='/path/search?one=1&two=2',
        children='Keresés indítása'
    ),
    html.Br(),
    dcc.Link(
        href='/path/?hello=HELLO#hash_string',
        children='Hash alapú oldalra navigálás'
    ),
    html.Br(),
    html.H4("URL tulajdonságai:"),
    html.Div(id='location_output')
])


# Callback függvények
@app.callback(
    Output('location_output', 'children'),
    Input('location', 'pathname'),
    Input('location', 'search'),
    Input('location', 'href'),
    Input('location', 'hash'),
)
def show_url_parts(pathname, search, href, hash_):
    return html.Div([
        html.Pre([
            f"""
            href: {href}
            path: {pathname}
            search: {search}
            hash: {hash_}
            """
        ])
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
