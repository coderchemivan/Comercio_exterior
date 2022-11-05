import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ClientsideFunction

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Clinical Analytics Dashboard"

server = app.server
app.config.suppress_callback_exceptions = True

# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()



def generate_control_card():
    """

    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P("Select a region"),
            dcc.Dropdown(
                id="clinic-select",
                options=[{"label": i, "value": i} for i in range(10)],
                value='Region',
                placeholder='America',
            ),
            html.Br(),
            html.Br(),
            html.P("Select a country"),
            dcc.Dropdown(
                id="admit-select",
                options=[{"label": i, "value": i} for i in range(10)],
                #alue=admit_list[:],
                multi=True,
                placeholder="USA",
            ),
            html.Br(),
            html.P("Select a product"),
            dcc.Dropdown(
                id="admit-select1",
                options=[{"label": i, "value": i} for i in range(10)],
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
                            
                        dcc.Graph(id="patient_volume_hm"),
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
                                dcc.Graph(id = 'death', config={'displayModeBar': False}, className='dcc_compon',
                                                    style={'margin-top': '20px'})
                       
                            ],)
                        ],
                    ),
                    html.Div(
                        id="wait_time_card2",
                        className="six columns",
                        children=[
                            html.Hr(),
                            html.Div([
                                dcc.Graph(id = 'death3', config={'displayModeBar': False}, className='dcc_compon',
                                                    style={'margin-top': '15px'})
                                                    
                            ],)
                        ],
                    ),

                ],),
            ],
        )
    ],
)




# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
