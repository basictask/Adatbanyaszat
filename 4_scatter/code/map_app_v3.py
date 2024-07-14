import os
import map_app_v2
import pandas as pd
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output

current_dir = os.path.dirname(os.path.abspath(__file__))
series = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsSeries.csv'), low_memory=False)
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(
    style={'padding': '20px'},
    children=map_app_v2.app.layout.children + [  # Előző alkalmazás layout komponense
        # Új komponensek hozzáadása az előző alkalmazás elrendezésén túl
        html.Div(style={'marginBottom': '20px'}),  # Vertikális hely a két komponens között
        dcc.Dropdown(
            id='indicator_dropdown',
            value='GINI index (World Bank estimate)',
            options=[{'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]]
        ),
        dbc.Row(
            dbc.Col(
                [
                    dcc.Markdown(
                        id='indicator_map_details_md',
                    )
                ],
                width=12,
            )
        ),
    ]
)


# Előző alkalmazás callback függvényei
map_app_v2.register_callbacks(app)


@app.callback(
    Output('indicator_map_details_md', 'children'),
    Input("indicator_dropdown", "value"),
)
def update_indicator_map_details_md(indicator):
    """
    Frissíti a MarkDown komponens értékét a legördülő menü állapotának változására
    """
    # Adatkészlet beolvasása
    series_df = series[series['Indicator Name'].eq(indicator)]
    if series_df.empty:
        markdown = "Nincs elérhető adat az indikátorról"
    else:
        limitations = series_df['Limitations and exceptions'].fillna('N/A').str.replace('\n\n', '').values[0]
        # Markdown komponens szövegének definiálása
        markdown = f"""
            ---
            ## {series_df['Indicator Name'].values[0]}
            {series_df['Long definition'].values[0]}
            * **Mértékegység:** {series_df['Unit of measure'].fillna('count').values[0]}
            * **Periodicitás:** {series_df['Periodicity'].fillna('N/A').values[0]}
            * **Forrás:** {series_df['Source'].values[0]}
            ### Limitációk és kivételek: 
            {limitations}
        """
    return markdown


if __name__ == '__main__':
    app.run_server(debug=True)
