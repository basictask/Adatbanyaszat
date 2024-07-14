import warnings
import pandas as pd
import plotly.express as px
from pandas_datareader import wb
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State

warnings.simplefilter(action='ignore', category=FutureWarning)

indicators = {
    "IT.NET.USER.ZS": "Internetet használók aránya (teljes népesség %)",
    "SG.GEN.PARL.ZS": "A nemzeti parlamentekben a nők által betöltött helyek aránya (%)",
    "EN.ATM.CO2E.KT": "CO2-kibocsátás (kt)",
}

# Országnév és ISO ID lekérdezése a tematikus térképezéshez
countries = wb.get_countries()
countries["capitalCity"] = countries["capitalCity"].replace({"": None})
countries.dropna(subset=["capitalCity"], inplace=True)
countries = countries[["name", "iso3c"]]
countries = countries[countries["name"] != "Kosovo"]
countries = countries.rename(columns={"name": "country"})


def update_wb_data():
    # Világbanki adatok lekérdezése API-ról
    df = wb.download(
        indicator=(list(indicators)), country=countries["iso3c"], start=2005, end=2016, errors="warn"
    )
    df = df.reset_index()
    df.year = df.year.astype(int)
    # ISO3 oszlop hozzáadása az eredeti adatkészlethez
    df = pd.merge(df, countries, on="country")
    df = df.rename(columns=indicators)
    return df


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    style={'padding': '20px'},
    children=[
        dbc.Row(
            dbc.Col(
                [
                    html.H1(
                        "A Világbank országadatainak összehasonlítása",
                        style={"textAlign": "center"},
                    ),
                    dcc.Graph(id="choropleth_map", figure={}),
                ],
                width=12,
            )
        ),
        dbc.Row(
            dbc.Col(
                [
                    dbc.Label(
                        "Adatkészlet kiválasztása:",
                        className="fw-bold",
                        style={"textDecoration": "underline", "fontSize": 20},
                    ),
                    dcc.RadioItems(
                        id="radio_indicator",
                        options=[{"label": i, "value": i} for i in indicators.values()],
                        value=list(indicators.values())[0],
                        inputClassName="me-2",
                    ),
                ],
                width=4,
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label(
                            "Évek kiválasztása:",
                            className="fw-bold",
                            style={"textDecoration": "underline", "fontSize": 20},
                        ),
                        dcc.RangeSlider(
                            id="years_range",
                            min=2005,
                            max=2016,
                            step=1,
                            value=[2005, 2006],
                            marks={
                                2005: "2005",
                                2006: "'06",
                                2007: "'07",
                                2008: "'08",
                                2009: "'09",
                                2010: "'10",
                                2011: "'11",
                                2012: "'12",
                                2013: "'13",
                                2014: "'14",
                                2015: "'15",
                                2016: "2016",
                            },
                        ),
                        dbc.Button(
                            id="filter_button",
                            children="Szűrés",
                            n_clicks=0,
                            color="primary",
                            className="mt-4",
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        dcc.Store(id="storage", storage_type="session", data={}),
        dcc.Interval(id="timer", interval=1000 * 60, n_intervals=0),
    ]
)


def register_callbacks(param_app):
    """
    A register_callbacks() függvény kívülről meghívható. Ha egy másik paraméterül kapott alkalmazással meghívódik,
    a függvénytörzsben definiált callback függvények regisztrálódnak a paraméterül kapott alkalmazáshoz.
    """
    @param_app.callback(
        Output("storage", "data"),
        Input("timer", "n_intervals")
    )
    def store_data(_):
        """
        Ez a callback függvény a Timer komponens által kiváltott események hatására fut le,
        az eltelt időközök számának megfelelően. Lekéri a frissített adatokat az update_wb_data
        függvényből, és szótár formátumban tárolja azokat a Storage komponensben.
        """
        dataframe = update_wb_data()
        return dataframe.to_dict("records")

    @param_app.callback(
        Output("choropleth_map", "figure"),
        Input("filter_button", "n_clicks"),
        Input("storage", "data"),
        State("years_range", "value"),
        State("radio_indicator", "value"),
    )
    def update_graph(_, stored_dataframe, years_chosen, indct_chosen):
        dff = pd.DataFrame.from_records(stored_dataframe)
        print(years_chosen)

        if years_chosen[0] != years_chosen[1]:
            dff = dff[dff.year.between(years_chosen[0], years_chosen[1])]
            dff = dff.groupby(["iso3c", "country"])[indct_chosen].mean()
            dff = dff.reset_index()

        if years_chosen[0] == years_chosen[1]:
            dff = dff[dff["year"].isin(years_chosen)]

        fig = px.choropleth(
            data_frame=dff,
            locations="iso3c",
            color=indct_chosen,
            scope="world",
            hover_data={"iso3c": False, "country": True},
            labels={
                indicators["SG.GEN.PARL.ZS"]: "Nők aránya",
                indicators["IT.NET.USER.ZS"]: "Internethasználók aránya",
            },
        )
        fig.update_layout(
            geo={"projection": {"type": "natural earth"}},
            margin=dict(l=50, r=50, t=50, b=50),
        )
        return fig


# Callback föggvények hozzáadása az alkalmazáshoz
register_callbacks(app)


if __name__ == "__main__":
    app.run_server(debug=True)
