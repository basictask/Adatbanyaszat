import os
import dash
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import Input, Output, dcc, html

# Adatkészlet beolvasása
current_dir = os.path.dirname(os.path.abspath(__file__))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)

# Alkalmazás példányosítása
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

app.layout = html.Div(
    style={'padding': '20px'},
    children=[
        dbc.Label('Indikátor kiválasztása:'),
        dcc.Dropdown(
            id='hist_indicator_dropdown',
            placeholder='index (World Bank estimate)',
            options=[{'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]]
        ),
        html.Div(style={'height': '20px'}),  # Vertikális térköz
        dbc.Label('Évek kiválasztása:'),
        dcc.Dropdown(
            id='hist_multi_year_selector',
            multi=True,
            value=[2015],
            placeholder='Válasszon egy vagy több évet',
            options=[{'label': year, 'value': year} for year in poverty['year'].drop_duplicates().sort_values()]
        ),
        html.Div(style={'height': '20px'}),
        dbc.Label('Osztályközök számának kiválasztása:'),
        dcc.Slider(
            id='hist_bins_slider',
            min=0,
            step=5,
            marks={x: str(x) for x in range(0, 105, 5)}
        ),
        html.Div(style={'height': '20px'}),
        dcc.Graph(id='indicator_year_histogram')
    ]
)


@app.callback(
    Output('indicator_year_histogram', 'figure'),
    Input('hist_multi_year_selector', 'value'),
    Input('hist_indicator_dropdown', 'value'),
    Input('hist_bins_slider', 'value')
)
def display_histogram(years, indicator, nbins):
    """
    Frissíti a hisztogramm ábrát a kiválasztott évek, indikátor és bins értékek alapján
    """
    if not years or not indicator:
        raise PreventUpdate
    if isinstance(years, int):
        years = [years]
    df = poverty[poverty['year'].isin(years) & poverty['is_country']]  # Adatkészlet szűrése
    fig = px.histogram(  # Hisztogram létrehozása
        df,
        x=indicator,
        color='year',
        facet_col='year',
        height=700,
        nbins=nbins,
    )
    fig.for_each_xaxis(lambda axis: axis.update(title=''))
    fig.add_annotation(
        text=indicator,
        y=-0.12,
        yref='paper'
    )
    return fig


# Alkalmazás futtatása
if __name__ == '__main__':
    app.run_server(debug=True)
