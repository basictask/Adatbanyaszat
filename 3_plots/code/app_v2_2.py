import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash import Input, Output
from get_data import get_poverty
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Adathalmaz betöltése
poverty = get_poverty()
gini = 'GINI index (World Bank estimate)'
gini_df = poverty[poverty[gini].notna()]

# Alkalmazás példányosítása
app = dash.Dash(__name__)

# FrontEnd komponensek
app.layout = html.Div([
    html.H2(
        'Gini Index - Világbank adatok',
        style={'textAlign': 'center'}
    ),
    dbc.Row([
        dbc.Col([
            # Legördülő menü az évnek
            dcc.Dropdown(
                id='gini_year_dropdown',
                options=[{'label': year, 'value': year} for year in gini_df['year'].drop_duplicates().sort_values()]
            ),
            dcc.Graph(id='gini_year_barchart')
        ]),
        dbc.Col([
            # Legördülő menü az országnak
            dcc.Dropdown(
                id='gini_country_dropdown',
                options=[{'label': country, 'value': country} for country in gini_df['Country Name'].unique()]
            ),
            dcc.Graph(id='gini_country_barchart')
        ])
    ])
])


def register_callbacks(param_app):
    @param_app.callback(
        Output('gini_year_barchart', 'figure'),
        Input('gini_year_dropdown', 'value')
    )
    def plot_gini_year_barchart(year):
        if not year:
            raise PreventUpdate
        df = gini_df[gini_df['year'].eq(year)].sort_values(gini).dropna(subset=[gini])
        n_countries = len(df['Country Name'])
        fig = px.bar(
            df,
            x=gini,
            y='Country Name',
            orientation='h',
            height=200 + (n_countries * 20),
            title=gini + ' ' + str(year)
        )
        return fig

    @param_app.callback(
        Output('gini_country_barchart', 'figure'),
        Input('gini_country_dropdown', 'value')
    )
    def plot_gini_country_barchart(country):
        if not country:
            raise PreventUpdate
        df = gini_df[gini_df['Country Name'] == country].dropna(subset=[gini])
        fig = px.bar(
            df,
            x='year',
            y=gini,
            title=' - '.join([gini, country])
        )
        return fig


register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)
