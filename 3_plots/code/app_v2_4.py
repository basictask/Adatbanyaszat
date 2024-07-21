"""
Az alkalmazás ezen verziója azt demonstrálja, hogyan lehet korábban definiált callback függvényeket és elrendezési
komponenseket többször felhasználni egy alkalmazásban.
"""
import dash
import app_v2_1  # Alkalmazás előző verziói
import app_v2_2
import app_v2_3
from dash import dcc
from dash import html
import plotly.express as px
from dash import Input, Output
from get_data import *
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# Adathalmaz előkészítése
poverty = get_poverty()
income_share_df = get_income_share_df()
income_share_cols = income_share_df.columns[:-2]

# Alkalmazás példányosítása
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    *app_v2_3.app.layout.children[:-1],  # Előző alkalmazás FrontEnd komponensei (* a kicsomagolás operátor)
    dbc.Row([  # Új komponens
        dbc.Col(lg=1),
        dbc.Col([
            html.H2('Jövedelmek megoszlása', style={'textAlign': 'center'}),
            html.Br(),
            dcc.Dropdown(
                id='income_share_country_dropdown',
                options=[{'label': country, 'value': country} for country in income_share_df['Country Name'].unique()]
            ),
            dcc.Graph(id='income_share_country_barchart')
        ], lg=10)
    ]),
    app_v2_3.app.layout.children[-1]  # Előző alkalmazás utolsó komponense
])


def register_callbacks(param_app):
    @param_app.callback(
        Output('income_share_country_barchart', 'figure'),
        Input('income_share_country_dropdown', 'value'),
    )
    def plot_income_share_barchart(country):  # Új callback függvény regisztrálása
        if country is None:
            raise PreventUpdate

        fig = px.bar(
            income_share_df[income_share_df['Country Name'] == country].dropna(),
            x=income_share_cols,
            y='Year',
            barmode='stack',
            height=600,
            hover_name='Country Name',
            title=f'Income Share Quintiles - {country}',
            orientation='h',
        )
        fig.layout.legend.title = None
        fig.layout.legend.orientation = 'h'
        fig.layout.legend.x = 0.2
        fig.layout.xaxis.title = None
        return fig


app_v2_1.register_callbacks(app)  # v2_1 alkalmazás callback függvényei
app_v2_2.register_callbacks(app)  # v2_2 alkalmazás callback függvényei
register_callbacks(app)  # Ezen alkalmazás callback függvénye

if __name__ == '__main__':
    app.run_server(debug=True)
