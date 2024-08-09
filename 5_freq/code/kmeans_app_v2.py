import os
import dash
import numpy as np
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, no_update

from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

cividis0 = px.colors.sequential.Cividis[0]

# Adatkészlet beolvasása
current_dir = os.path.dirname(os.path.abspath(__file__))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)

# Alkalmazás példányosítása
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO])


def spacer(h):  # Vertikális térköz
    return html.Div(style={'height': f'{h}px'})


app.layout = html.Div(
    style={'padding': '20px'},
    children=[
        html.H1('K-Közép klaszterezés indikátorok szerint', style={'textAlign': 'center'}),
        html.H4("Év kiválasztása:"),
        dcc.Slider(
            id='year_cluster_slider',
            min=poverty['year'].min(),
            max=poverty['year'].max(),
            step=1,
            included=False,
            value=poverty['year'].min(),
            marks={
                year: {'label': str(year), 'style': {'color': cividis0, 'fontSize': 14}}
                for year in range(poverty['year'].min(), poverty['year'].max() + 1, 5)
            }
        ),
        spacer(20),
        html.H4("Klaszterszám kiválasztása:"),
        dcc.Slider(
            id='ncluster_slider',
            min=2,
            max=21,
            step=1,
            value=2,
            marks={
                k: {'label': str(k), 'style': {'color': cividis0, 'fontSize': 14}} for k in range(2, 21)
            },
            included=False,
        ),
        spacer(20),
        html.H4("Indikátor kiválasztása:"),
        dcc.Dropdown(
            id='indicator_dropdown',
            placeholder='Indikátor kiválasztása',
            options=[{'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]]
        ),
        spacer(20),
        html.Div(
            children=[
                html.Button('Futtatás', id='kmeans_button')
            ],
            style={
                'display': 'flex',
                'justify-content': 'center',
                'align-items': 'center',
            }
        ),
        spacer(20),
        dcc.Loading([
            dcc.Graph(
               id='clustered_map_chart'
            ),
        ])
    ]
)


@app.callback(
    Output('clustered_map_chart', 'figure'),
    Input('kmeans_button', 'n_clicks'),
    State('year_cluster_slider', 'value'),
    State('ncluster_slider', 'value'),
    State('indicator_dropdown', 'value'),
)
def clustered_map(n_clicks, year, n_clusters, indicator):
    if not n_clicks:
        return no_update

    if not indicator or not year or not n_clusters:  # Ha nincs kiválasztva semmi a diagram nem fog frissülni
        return no_update

    # Adatkészlet leszűrése
    df = poverty[poverty['is_country'] & poverty['year'].eq(year)][[indicator, 'Country Name', 'year']]

    if df.isna().all().any():
        return px.scatter(
            title='No available data for the selected combination of year / indicator.'
        )

    data = df[indicator].to_frame()
    n_clusters = min(n_clusters, len(data.dropna()))  # Klaszterszám konzisztencia kritérium

    # Transzformációs eljárások inicializálása
    imp = SimpleImputer(missing_values=np.nan, strategy='mean')
    scaler = StandardScaler()
    kmeans = KMeans(n_clusters=n_clusters)

    # Transzformáció és gépi tanulás alkalmazása
    data_no_na = imp.fit_transform(data)
    scaled_data = scaler.fit_transform(data_no_na)
    kmeans.fit(scaled_data)

    # Diagram létrehozása
    fig = px.choropleth(
        df,
        locations='Country Name',
        locationmode='country names',
        color=[str(x) for x in kmeans.labels_],
        labels={'color': 'Cluster'},
        hover_data=indicator,
        height=650,
        title=f"Országok klaszterezése - {year}.<br>K: {n_clusters} Inercia: {round(kmeans.inertia_, 2)}",
        color_discrete_sequence=px.colors.qualitative.T10
    )

    # Diagram személyre szabása
    fig.layout.geo.showframe = False
    fig.layout.geo.showcountries = True
    fig.layout.geo.projection.type = 'natural earth'
    fig.layout.geo.lataxis.range = [-53, 76]
    fig.layout.geo.lonaxis.range = [-137, 168]
    fig.layout.geo.landcolor = 'white'
    # fig.layout.geo.bgcolor = '#E5ECF6'
    # fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.geo.countrycolor = 'gray'
    fig.layout.geo.coastlinecolor = 'gray'

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
