import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import pandas as pd 
import datetime
from datetime import datetime as dt
import pathlib
from data_processing.data_processing import Data

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Mexico Trade"

server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()



def generate_control_card():
    """:return: A Div containing controls for graphs.
    """
    
    regionsList = Data('world_trade').obtaincountriesProperties(nivel=2,region='America')
    productsList = Data('world_trade').obtainProductoDescription()
    
    regionsList = [region if len(region) < 20 else region[:10] + '...' for region in regionsList]
    productsList = [product if len(product) < 15 else product[:10] + '...' for product in productsList]
    return html.Div(
        id="control-card",
        children=[
            html.P("Select a region"),
            dcc.Dropdown(
                id="region-select",
                options=[{"label": i, "value": i} for i in regionsList],
                value='Region',
                placeholder='America',
            ),
            html.Br(),
            html.Br(),
            html.P("Select a country"),
            dcc.Dropdown(
                id="country-select",
                #options=[{"label": i, "value": i} for i in countriesList],
                #alue=admit_list[:],
                multi=False,
                placeholder="USA",
            ),
            html.Br(),
            html.P("product-select"),
            dcc.Dropdown(
                id="admit-select1",
                options=[{"label": i, "value": i} for i in productsList],
                #value=admit_list[:],
                multi=True,
                placeholder="Crudo",
            ),
            html.Br(),
            html.Br(),
            html.Div(
                id="reset-btn-outer1",
                children=html.Button(id="reset-btn", children="Importaciones", n_clicks=0),
            ),
            html.Br(),
            html.Div(
                id="reset-btn-outer2",
                children=html.Button(id="reset-btn2", children="Exportaciones", n_clicks=0),
            ),
            html.Br(),
            html.Div(
                id="filtro_button_outer",
                children=html.Button(id="filtro-btn", children="Aceptar", n_clicks=0),
            ),
        ],
    )
df = Data('world_trade',reporting_country='484',year=[2019],imp_exp=2).read_data()
app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[html.Img(src=app.get_asset_url("International-trade.png"))],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="three columns",
            children=[generate_control_card()]
            + [
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                # Patient Volume Heatmap
                html.Div(
                    id="patient_volume_card",
                    children=[
                        html.B("Importado en 2020"),
                        html.Hr(),
                        html.B('Año', className = 'fix_label', style = {'text-align': 'left', 'color': 'black'}),
                        dcc.RangeSlider(2010, 2022, value=[2015,2021], marks={
                            str(yr): str(yr) for yr in range(2010, 2022, 1)
                        }, className = 'dcc_compon'),
                            
                        dcc.Graph(id="treemap",config={'displayModeBar':True},style={'margin-top': '0px'},
                                figure=px.treemap(df,
                                path=['description','SA_4'],
                                values='tradevalue',
                                height=800, width=900)),
                    ],
                ),
                # Patient Wait time by Department
                html.Div([
                    html.Div(
                        id="wait_time_card",
                        className="six columns",
                        children=[
                            #html.B("Patient Wait Time and Satisfactory Scores"),
                            html.Hr(),
                            html.Div([
                                dcc.Graph(id = 'origen-destino',  config={'displayModeBar': False}, className='dcc_compon',
                                                    style={'margin-top': '15px'}
                                )
                            ],)
                        ],
                    ),
                    html.Div(
                        id="wait_time_card2",
                        className="six columns",
                        children=[
                            html.Hr(),
                            html.Div([
                                dcc.Graph(id = 'indicador', config={'displayModeBar': False}, className='dcc_compon',
                                                    style={'margin-top': '15px'})
                                                    
                            ],)
                        ],
                    ),

                ],),
            ],
        )
    ],
)

@app.callback(Output(component_id='country-select',component_property='options'),
            Output(component_id='country-select',component_property='placeholder'),
              [Input('region-select','value')])
def paises_por_region(region_select):
    print(region_select)
    countriesList = Data('world_trade').obtaincountriesProperties(nivel=1,region=region_select)
    countriesList = [country if len(country) < 10 else country[:10] + '...' for country in countriesList]
    placeholder = "EUA"
    if region_select == 'America':
        placeholder = 'USA'
    elif region_select == 'Asia':
        placeholder = 'China'
    elif region_select == 'Africa':
        placeholder = 'Nigeria'
    elif region_select == 'Europe':
        placeholder = 'Germany'
    elif region_select == 'Oceania':
        placeholder = 'Australia'
    return [{"label": i, "value": i} for i in countriesList], placeholder


@app.callback(Output(component_id='origen-destino',component_property='figure')
                ,Input('filtro-btn','n_clicks'))
def filtro(n_clicks):
    print(n_clicks)
    df = Data('world_trade',reporting_country='484',year=[2019],imp_exp=2).read_data()
    fig = px.choropleth(df,
                        locations="iso_3",
                        color='tradevalue',
                        hover_name="name",
                        scope='world',
                        projection='natural earth'
                        ).update_traces(showlegend=False).update_layout(margin=dict(t=25, r=0, l=5, b=20))
    return fig
# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)

