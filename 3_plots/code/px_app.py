import dash
from dash import dcc
from dash import html
import plotly.express as px
from get_data import get_poverty
import dash_bootstrap_components as dbc

# Szűrési változók
YEAR = 2010
INDICATOR = 'Population, total'
GROUPER = 'Region'

# Adathalmaz betöltése
poverty = get_poverty()

# Adathalmaz szűrése
df = (poverty[poverty['year'].eq(YEAR)].sort_values(INDICATOR).dropna(subset=[INDICATOR, GROUPER]))

# Dash alkalmazás létrehozása
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Graph(figure=px.scatter(
        data_frame=df,
        x=INDICATOR,
        y='Country Name',
        color=GROUPER,
        symbol=GROUPER,
        log_x=True,
        hover_name=df['Short Name'] + ' ' + df['flag'],
        size=[1] * len(df),
        title=' '.join([INDICATOR, 'by', GROUPER, str(YEAR)]),
        height=700
    ))
])

if __name__ == '__main__':
    app.run_server(debug=True)
