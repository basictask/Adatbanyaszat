import os
import re
import dash
import numpy as np
import pandas as pd
import plotly.express as px
from urllib.parse import unquote
import plotly.graph_objects as go
from sklearn.cluster import KMeans
import dash_bootstrap_components as dbc
from sklearn.impute import SimpleImputer
from dash.exceptions import PreventUpdate
from sklearn.preprocessing import StandardScaler
from dash import dash_table, dcc, html, Input, Output, State


app = dash.Dash(
    __name__,
    meta_tags=[{
            'name': 'viewport',
            'content': 'width=device-width, initial-scale=1.0, maximum-scale=4, minimum-scale=0.5,'
    }],
    external_stylesheets=[dbc.themes.COSMO]
)
server = app.server

# Adatkészletek betöltése
current_dir = os.path.dirname(os.path.abspath(__file__))
poverty_data = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsData.csv'))
poverty = pd.read_csv(os.path.join(current_dir, '../../data/poverty.csv'), low_memory=False)
series = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsSeries.csv'), low_memory=False)
country_df = pd.read_csv(os.path.join(current_dir, '../../data/PovStatsCountry.csv')).drop(['Unnamed: 30'], axis=1)

gini = 'GINI index (World Bank estimate)'
gini_df = poverty[poverty[gini].notna()]

regions = [
    'East Asia & Pacific', 'Europe & Central Asia', 'Fragile and conflict affected situations', 'High income',
    'IDA countries classified as fragile situations', 'IDA total', 'Latin America & Caribbean', 'Low & middle income',
    'Low income', 'Lower middle income', 'Middle East & North Africa', 'Middle income', 'South Asia',
    'Sub-Saharan Africa', 'Upper middle income', 'World'
]

population_df = poverty_data[
    ~poverty_data['Country Name'].isin(regions) & (poverty_data['Indicator Name'] == 'Population, total')
]

income_share_df = poverty.filter(regex='Country Name|^year$|Income share.*?20').dropna()
income_share_df = income_share_df.rename(columns={
    'Income share held by lowest 20%': '1 Income share held by lowest 20%',
    'Income share held by second 20%': '2 Income share held by second 20%',
    'Income share held by third 20%': '3 Income share held by third 20%',
    'Income share held by fourth 20%': '4 Income share held by fourth 20%',
    'Income share held by highest 20%': '5 Income share held by highest 20%'
}).sort_index(axis=1)
income_share_df.columns = [re.sub(r'\d Income share held by ', '', col).title() for col in income_share_df.columns]
income_share_cols = income_share_df.columns[:-2]

perc_pov_cols = poverty.filter(regex='Poverty gap').columns
perc_pov_df = poverty[poverty['is_country']].dropna(subset=perc_pov_cols)
perc_pov_years = sorted(set(perc_pov_df['year']))

countries = poverty[poverty['is_country']]['Country Name'].drop_duplicates().sort_values().tolist()
cividis0 = px.colors.sequential.Cividis[0]


def make_empty_fig():
    fig = go.Figure()
    fig.layout.paper_bgcolor = '#E5ECF6'
    fig.layout.plot_bgcolor = '#E5ECF6'
    return fig


def multiline_indicator(indicator):
    final = []
    split = indicator.split()
    for i in range(0, len(split), 3):
        final.append(' '.join(split[i:i + 3]))
    return '<br>'.join(final)


# Fő elrendezés
main_layout = html.Div([
    html.Div([
        dbc.NavbarSimple([
            dbc.DropdownMenu(
                [dbc.DropdownMenuItem(country, href=country) for country in countries],
                label='Ország kiválasztása'
            ),
        ], brand='Home', brand_href='/'),
        dcc.Location(id='location'),
        html.Div(id='main_content'),
        html.Br(),
        dbc.Row([
            dbc.Col(lg=1),
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab([
                        html.Ul([
                            html.Br(),
                            html.Li('Gazdaságok száma: 170'),
                            html.Li('Időbeli lefedettség: 1974 - 2019'),
                            html.Li('Frissítési gyakoriság: Negyedéves'),
                            html.Li('Utolsó frissítés: 2020. március 18.'),
                            html.Li([
                                'Source: ',
                                html.A(
                                    'https://datacatalog.worldbank.org/dataset/poverty-and-equity-database',
                                    href='https://datacatalog.worldbank.org/dataset/poverty-and-equity-database'
                                )
                            ])
                        ])
                    ], label='Kulcsfontosságú tények'),
                    dbc.Tab([
                        html.Ul([
                            html.Br(),
                            html.Li([
                                'A projekt GitHub tárhelye: ',
                                html.A(
                                    'https://github.com/basictask/Adatbanyaszat',
                                    href='https://github.com/basictask/Adatbanyaszat'
                                )
                            ])
                        ])
                    ], label='Projekt információk')
                ]),
            ])
        ])
    ], style={'backgroundColor': '#E5ECF6'})
])

# Országok műszerfala
country_dashboard = html.Div([
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            html.Br(),
            html.H1(id='country_heading'),
            dbc.Row([
                dbc.Col(dcc.Graph(id='country_page_graph'))
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label('Indikátor kiválasztása:'),
                    dcc.Dropdown(
                        id='country_page_indicator_dropdown',
                        placeholder='Indiktátor kiválasztása',
                        value='Population, total',
                        options=[{'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]]
                    ),
                ], lg=6, md=11),
                dbc.Col([
                    dbc.Label('Országok kiválasztása:'),
                    dcc.Dropdown(
                        id='country_page_contry_dropdown',
                        placeholder='Egy vagy több ország kiválasztása az összehasonlításhoz',
                        multi=True,
                        options=[{'label': c, 'value': c} for c in countries]
                    ),
                ], lg=6, md=11)
            ]),
            html.Br(),
            html.Br(),
            html.Div(id='country_table')
        ], lg=10)
    ]),
])

# Indikátorok műszerfala
indicators_dashboard = html.Div([
    dbc.Col([
        html.Br(),
        html.H1('Szegénység és egyenlőség adatbázis'),
        html.H2('Világbank'),
    ], style={'textAlign': 'center'}),
    html.Br(),
    dbc.Row([
        dbc.Col(lg=2),
        dbc.Col([
            dbc.Tabs([
                dbc.Tab([
                    html.Br(),
                    dcc.Dropdown(
                        id='indicator_dropdown',
                        value='GINI index (Világbank becslése)',
                        placeholder="Indikátor kiválasztása",
                        options=[{'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]]
                    ),
                    dcc.Graph(id='indicator_map_chart'),
                    dcc.Markdown(
                        id='indicator_map_details_md',
                        style={'backgroundColor': '#E5ECF6'}
                    )
                ], label='Metrikák felfedezése'),
                dbc.Tab([
                    html.Br(),
                    dbc.Row([
                        dbc.Col(lg=1),
                        dbc.Col([
                            dbc.Label('Év kiválasztása:'),
                            dcc.Slider(
                                id='year_cluster_slider',
                                min=1974,
                                max=2018,
                                step=1,
                                included=False,
                                value=2018,
                                marks={year: str(year) for year in range(1974, 2019, 5)}
                            )
                        ], lg=6, md=12),
                        dbc.Col([
                            dbc.Label('Klaszterek számának kiválasztása:'),
                            dcc.Slider(
                                id='ncluster_cluster_slider',
                                min=2,
                                max=15,
                                step=1,
                                included=False,
                                value=2,
                                marks={n: str(n) for n in range(2, 16)}
                            ),
                        ], lg=4, md=12)
                    ]),
                    html.Br(),
                    dbc.Row([
                        dbc.Col(lg=1),
                        dbc.Col([
                            dbc.Label('Indikátor kiválasztása:'),
                            dcc.Dropdown(
                                id='cluster_indicator_dropdown',
                                optionHeight=40,
                                multi=True,
                                value=['Population, total'],
                                placeholder='Indikátor kiválasztása',
                                options=[
                                    {'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]
                                ]
                            ),
                        ], lg=6),
                        dbc.Col([
                            dbc.Label(''),
                            html.Br(),
                            dbc.Button("Futtatás", id='clustering_submit_button'),
                        ]),
                    ]),
                    dcc.Loading([
                        dcc.Graph(id='clustered_map_chart')
                    ])
                ], label='Országok Klaszterezése'),
            ]),
        ], lg=8)
    ]),
    html.Br(),
    html.Br(),
    html.Hr(),
    dbc.Row([
        dbc.Col(lg=2),
        dbc.Col([
            dbc.Label('Indikátor:'),
            dcc.Dropdown(
                id='hist_indicator_dropdown',
                optionHeight=40,
                value='GINI index (Világbank becslése)',
                placeholder='Indikátor kiválasztása',
                options=[{'label': indicator, 'value': indicator} for indicator in poverty.columns[3:54]]
            ),
        ], lg=5),
        dbc.Col([
            dbc.Label('Évek:'),
            dcc.Dropdown(
                id='hist_multi_year_selector',
                multi=True,
                value=[2015],
                placeholder='Egy vagy több év kiválasztása',
                options=[{'label': year, 'value': year} for year in poverty['year'].drop_duplicates().sort_values()]
            ),
        ], lg=3),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(lg=2),
        dbc.Col([
            html.Br(),
            dbc.Label('Osztályközök számának módosítása:'),
            dcc.Slider(
                id='hist_bins_slider',
                dots=True,
                min=0,
                max=100,
                step=5,
                included=False,
                marks={x: str(x) for x in range(0, 105, 5)}
            ),
            dcc.Graph(id='indicator_year_histogram', figure=make_empty_fig()),
        ], lg=8)
    ]),
    dbc.Row([
        dbc.Col(lg=2),
        dbc.Col([
            html.Div(id='table_histogram_output'),
            html.Br(),
            html.Br(),
        ], lg=8)
    ]),
    html.H2('Gini Index - Világbank adatai', style={'textAlign': 'center'}),
    html.Br(),
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            dbc.Label('Év:'),
            dcc.Dropdown(
                id='gini_year_dropdown',
                placeholder='Év kiválasztása',
                options=[{'label': year, 'value': year} for year in gini_df['year'].drop_duplicates().sort_values()]
            ),
            html.Br(),
            dcc.Graph(
                id='gini_year_barchart',
                figure=make_empty_fig()
            )
        ], md=12, lg=5),
        dbc.Col([
            dbc.Label('Országok:'),
            dcc.Dropdown(
                id='gini_country_dropdown',
                placeholder='Egy vagy több ország kiválasztása',
                multi=True,
                options=[{'label': country, 'value': country} for country in gini_df['Country Name'].unique()]
            ),
            html.Br(),
            dcc.Graph(
                id='gini_country_barchart',
                figure=make_empty_fig()
            )
        ], md=12, lg=5),
    ]),
    dbc.Row([
        dbc.Col(lg=2),
        dbc.Col([
            html.Br(),
            html.H2('Jövedelmek megoszlása', style={'textAlign': 'center'}),
            html.Br(),
            dbc.Label('Ország:'),
            dcc.Dropdown(
                id='income_share_country_dropdown',
                placeholder='Ország kiválasztása',
                options=[{'label': country, 'value': country} for country in income_share_df['Country Name'].unique()]
            ),
            dcc.Graph(
                id='income_share_country_barchart',
                figure=make_empty_fig()
            )
        ], lg=8)
    ]),
    html.Br(),
    html.H2('Szegénységi szakadék 1,9, 3,2 és 5,5 USD (a népesség %-ában)', style={'textAlign': 'center'}),
    html.Br(), html.Br(),
    dbc.Row([
        dbc.Col(lg=2),
        dbc.Col([
            dbc.Label('Szegénységi szint:'),
            dcc.Slider(
                id='perc_pov_indicator_slider',
                min=0,
                max=2,
                step=1,
                included=False,
                value=0,
                marks={
                    0: {'label': '$1.9', 'style': {'color': cividis0, 'fontWeight': 'bold', 'fontSize': 15}},
                    1: {'label': '$3.2', 'style': {'color': cividis0, 'fontWeight': 'bold', 'fontSize': 15}},
                    2: {'label': '$5.5', 'style': {'color': cividis0, 'fontWeight': 'bold', 'fontSize': 15}},
                }
            ),
        ], lg=2),
        dbc.Col([
            dbc.Label('Év:'),
            dcc.Slider(
                id='perc_pov_year_slider',
                min=perc_pov_years[0],
                max=perc_pov_years[-1],
                step=1,
                included=False,
                value=2018,
                marks={
                    year: {
                        'label': str(year),
                        'style': {'color': cividis0, 'fontSize': 14}
                    } for year in perc_pov_years[::5]
                }
            ),
        ], lg=5),
    ]),
    dbc.Row([
        dbc.Col(lg=1),
        dbc.Col([
            dcc.Graph(
                id='perc_pov_scatter_chart',
                figure=make_empty_fig()
            )
        ], lg=10)
    ]),
], style={'backgroundColor': '#E5ECF6'})

# Validációs elrendezés
app.validation_layout = html.Div([
    main_layout,
    indicators_dashboard,
    country_dashboard,
])


def register_callbacks(param_app):
    """
    Callback függvények regisztrációja a paraméterül megkapott alkalmazáshoz
    """
    @param_app.callback(
        Output('main_content', 'children'),
        Input('location', 'pathname')
    )
    def display_content(pathname):
        if unquote(pathname[1:]) in countries:
            return country_dashboard
        else:
            return indicators_dashboard

    @param_app.callback(
        Output('indicator_map_chart', 'figure'),
        Output('indicator_map_details_md', 'children'),
        Input('indicator_dropdown', 'value')
    )
    def display_generic_map_chart(indicator):
        if indicator is None:
            raise PreventUpdate
        df = poverty[poverty['is_country']]
        fig = px.choropleth(
            df,
            locations='Country Code',
            color=indicator,
            title=indicator,
            hover_name='Country Name',
            color_continuous_scale='cividis',
            animation_frame='year',
            height=650
        )
        fig.layout.geo.showframe = False
        fig.layout.geo.showcountries = True
        fig.layout.geo.projection.type = 'natural earth'
        fig.layout.geo.lataxis.range = [-53, 76]
        fig.layout.geo.lonaxis.range = [-138, 167]
        fig.layout.geo.landcolor = 'white'
        fig.layout.geo.bgcolor = '#E5ECF6'
        fig.layout.paper_bgcolor = '#E5ECF6'
        fig.layout.geo.countrycolor = 'gray'
        fig.layout.geo.coastlinecolor = 'gray'
        fig.layout.coloraxis.colorbar.title = multiline_indicator(indicator)

        series_df = series[series['Indicator Name'].eq(indicator)]
        if series_df.empty:
            markdown = "Nincs elérhető adat az indikátorhoz"
        else:
            limitations = series_df['Limitations and exceptions'].fillna('N/A').str.replace('\n\n', ' ').values[0]

            markdown = f"""
            ## {series_df['Indicator Name'].values[0]}  
    
            {series_df['Long definition'].values[0]}  
    
            * **Mértékegység** {series_df['Unit of measure'].fillna('count').values[0]}
            * **Periodicitás** {series_df['Periodicity'].fillna('N/A').values[0]}
            * **Forrás** {series_df['Source'].values[0]}
    
            ### Limitációk és kivételek:  
    
            {limitations}  
    
            """
        return fig, markdown

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
        fig.layout.paper_bgcolor = '#E5ECF6'
        return fig

    @param_app.callback(
        Output('gini_country_barchart', 'figure'),
        Input('gini_country_dropdown', 'value')
    )
    def plot_gini_country_barchart(countries_lst):
        if not countries_lst:
            raise PreventUpdate
        df = gini_df[gini_df['Country Name'].isin(countries_lst)].dropna(subset=[gini])
        fig = px.bar(
            df,
            x='year',
            y=gini,
            height=100 + (250 * len(countries_lst)),
            facet_row='Country Name',
            color='Country Name',
            labels={gini: 'Gini Index'},
            title=''.join([gini, '<br><b>', ', '.join(countries_lst), '</b>'])
        )
        fig.layout.paper_bgcolor = '#E5ECF6'
        return fig

    @param_app.callback(
        Output('income_share_country_barchart', 'figure'),
        Input('income_share_country_dropdown', 'value')
    )
    def plot_income_share_barchart(country):
        if country is None:
            raise PreventUpdate
        fig = px.bar(
            income_share_df[income_share_df['Country Name'] == country].dropna(),
            x=income_share_cols,
            y='Year',
            barmode='stack',
            height=600,
            hover_name='Country Name',
            title=f'Jövedelemhányad Kvintilisek - {country}',
            orientation='h'
        )
        fig.layout.legend.title = None
        fig.layout.legend.orientation = 'h'
        fig.layout.legend.x = 0.2
        fig.layout.legend.y = -0.15
        fig.layout.xaxis.title = 'A teljes jövedelem százalékos aránya'
        fig.layout.paper_bgcolor = '#E5ECF6'
        fig.layout.plot_bgcolor = '#E5ECF6'
        return fig

    @param_app.callback(
        Output('perc_pov_scatter_chart', 'figure'),
        Input('perc_pov_year_slider', 'value'),
        Input('perc_pov_indicator_slider', 'value')
    )
    def plot_perc_pov_chart(year, indicator):
        indicator = perc_pov_cols[indicator]
        df = perc_pov_df[perc_pov_df['year'].eq(year)].dropna(subset=[indicator]).sort_values(indicator)
        if df.empty:
            raise PreventUpdate

        fig = px.scatter(
            df,
            x=indicator,
            y='Country Name',
            color='Population, total',
            size=[30] * len(df),
            size_max=15,
            hover_name='Country Name',
            height=250 + (20 * len(df)),
            color_continuous_scale='cividis',
            title=indicator + '<b>: ' + f'{year}' + '</b>'
        )
        fig.layout.paper_bgcolor = '#E5ECF6'
        fig.layout.xaxis.ticksuffix = '%'
        return fig

    @param_app.callback(
        Output('indicator_year_histogram', 'figure'),
        Output('table_histogram_output', 'children'),
        Input('hist_multi_year_selector', 'value'),
        Input('hist_indicator_dropdown', 'value'),
        Input('hist_bins_slider', 'value')
    )
    def display_histogram(years, indicator, nbins):
        if (not years) or (not indicator):
            raise PreventUpdate
        df = poverty[poverty['year'].isin(years) & poverty['is_country']]
        fig = px.histogram(
            df,
            x=indicator,
            facet_col='year',
            color='year',
            title=indicator + ' Hisztogram',
            nbins=nbins,
            facet_col_wrap=4,
            height=700
        )
        fig.for_each_xaxis(lambda axis: axis.update(title=''))
        fig.add_annotation(
            text=indicator,
            x=0.5,
            y=-0.12,
            xref='paper',
            yref='paper',
            showarrow=False
        )
        fig.layout.paper_bgcolor = '#E5ECF6'

        table = dash_table.DataTable(
            columns=[{'name': col, 'id': col} for col in df[['Country Name', 'year', indicator]].columns],
            data=df[['Country Name', 'year', indicator]].to_dict('records'),
            style_header={'whiteSpace': 'normal'},
            fixed_rows={'headers': True},
            virtualization=True,
            style_table={'height': '400px'},
            sort_action='native',
            filter_action='native',
            export_format='csv',
            style_cell={'minWidth': '150px'}
        ),
        return fig, table

    @param_app.callback(
        Output('clustered_map_chart', 'figure'),
        Input('clustering_submit_button', 'n_clicks'),
        State('year_cluster_slider', 'value'),
        State('ncluster_cluster_slider', 'value'),
        State('cluster_indicator_dropdown', 'value')
    )
    def clustered_map(_, year, n_clusters, indicators):
        if not indicators:
            raise PreventUpdate
        imp = SimpleImputer(missing_values=np.nan, strategy='mean')
        scaler = StandardScaler()
        kmeans = KMeans(n_clusters=n_clusters)

        df = poverty[poverty['is_country'] & poverty['year'].eq(year)][indicators + ['Country Name', 'year']]
        data = df[indicators]

        if df.isna().all().any():
            return px.scatter(
                title='A kiválasztott év és mutatók kombinációjára vonatkozóan nem állnak rendelkezésre adatok'
            )

        data_no_na = imp.fit_transform(data)
        scaled_data = scaler.fit_transform(data_no_na)
        kmeans.fit(scaled_data)

        fig = px.choropleth(
            df,
            locations='Country Name',
            locationmode='country names',
            color=[str(x) for x in kmeans.labels_],
            labels={'color': 'Cluster'},
            hover_data=indicators,
            height=650,
            title=f'Országok klaszterei - {year}. Klaszterek száma: {n_clusters}<br>Inercia: {kmeans.inertia_:,.2f}',
            color_discrete_sequence=px.colors.qualitative.T10
        )
        fig.add_annotation(
            x=-0.1,
            y=-0.15,
            xref='paper',
            yref='paper',
            text='Indikátorok:<br>' + "<br>".join(indicators),
            showarrow=False
        )
        fig.layout.geo.showframe = False
        fig.layout.geo.showcountries = True
        fig.layout.geo.projection.type = 'natural earth'
        fig.layout.geo.lataxis.range = [-53, 76]
        fig.layout.geo.lonaxis.range = [-137, 168]
        fig.layout.geo.landcolor = 'white'
        fig.layout.geo.bgcolor = '#E5ECF6'
        fig.layout.paper_bgcolor = '#E5ECF6'
        fig.layout.geo.countrycolor = 'gray'
        fig.layout.geo.coastlinecolor = 'gray'
        return fig

    @param_app.callback(
        Output('country_page_contry_dropdown', 'value'),
        Input('location', 'pathname')
    )
    def set_dropdown_values(pathname):
        if unquote(pathname[1:]) in countries:
            country = unquote(pathname[1:])
            return [country]

    @param_app.callback(
        Output('country_heading', 'children'),
        Output('country_page_graph', 'figure'),
        Output('country_table', 'children'),
        Input('location', 'pathname'),
        Input('country_page_contry_dropdown', 'value'),
        Input('country_page_indicator_dropdown', 'value')
    )
    def plot_country_charts(pathname, countries_lst, indicator):
        if (not countries_lst) or (not indicator):
            raise PreventUpdate

        country = ''
        if unquote(pathname[1:]) in countries_lst:
            country = unquote(pathname[1:])

        df = poverty[poverty['is_country'] & poverty['Country Name'].isin(countries_lst)]
        fig = px.line(
            df,
            x='year',
            y=indicator,
            title='<b>' + indicator + '</b><br>' + ', '.join(countries_lst),
            color='Country Name'
        )
        fig.layout.paper_bgcolor = '#E5ECF6'
        table = country_df[country_df['Short Name'] == countries_lst[0]].T.reset_index()

        if table.shape[1] == 2:
            table.columns = [countries_lst[0] + ' Info', '']
            table = dbc.Table.from_dataframe(table)
        else:
            table = html.Div([html.Br() for _ in range(20)])

        return country + ' Poverty Data', fig, table


# Kezdeti elrendezés hozzárendelése az alkalmazáshoz
app.layout = main_layout
# Callback függvények regisztrálása
register_callbacks(app)


if __name__ == '__main__':
    app.run_server(debug=True)
