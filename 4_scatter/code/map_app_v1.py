import os
import dash
import pandas as pd
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output

current_dir = os.path.dirname(os.path.abspath(__file__))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)
year = 2016
indicator = 'GINI index (World Bank estimate)'


def multiline_indicator(indicator_name):
    """
    Mivel az indikátornevek hosszúak lehetnek, ez eltorzítja a diagram elrendezését, ha egy sorban van kiírva.
    Ez a függvény tördeli az indikátor neveket, hogy jobban ráférjen a diagramra.
    """
    final = []
    split = indicator_name.split()
    for i in range(0, len(split), 3):
        final.append(' '.join(split[i:i+3]))
    return '<br>'.join(final)


app = dash.Dash(__name__)

# Alkalmazás elrendezése
app.layout = html.Div([
    dcc.Dropdown(
        id='indicator_dropdown',
        value='GINI index (World Bank estimate)',
        options=[{'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]]
    ),
    dcc.Graph(id='indicator_map_chart')  # Üres térkép létrehozása
])


@app.callback(
    Output('indicator_map_chart', 'figure'),
    Input('indicator_dropdown', 'value')
)
def display_map_chart(indicator_name):
    """
    Callback függvény a térkép komponens megjelenítéséhez
    """
    df = poverty[poverty['is_country']]
    fig = px.choropleth(
        df,
        locations='Country Code',
        color=indicator_name,
        title=indicator_name,
        hover_name='Country Name',
        color_continuous_scale='cividis',
        animation_frame='year',
        height=650
    )
    fig.layout.geo.showframe = False
    fig.layout.coloraxis.colorbar.title = multiline_indicator(indicator_name)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
