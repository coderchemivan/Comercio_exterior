import dash
from dash import dcc
from dash import html
from dash import Dash, html, Input, Output, ctx
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
import pandas as pd 
import datetime
from datetime import datetime as dt
import pathlib
from data_processing.data_processing import Data
from plotly.subplots import make_subplots

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
                id="region_select",
                options=[{"label": i, "value": i} for i in regionsList],
                value='North America',
                placeholder='North America',
            ),
            html.Br(),
            html.P("Select a country"),
            dcc.Dropdown(
                id="country_select",
                #options=[{"label": i, "value": i} for i in countriesList],
                value="United States of America",
                multi=True,
                placeholder="United States of America",
            ),
            html.Br(),
            html.P("Select a product"),
            dcc.Dropdown(
                id="product-select",
                options=[{"label": i, "value": i} for i in productsList],
                #value='Animales vivos',
                multi=True,
                placeholder="Crudo",
            ),
            html.Br(),
            html.P("Indicator"),
            dcc.Dropdown(
                id="indicador-select",
                options={'linea de tiempo': 'Linea de tiempo', 'crecimiento': 'Crecimiento'},
                #value='Animales vivos',
                multi=False,
                placeholder="Crudo",
            ),
            html.Br(),
            html.Br(),
            html.Div(
                id="import-btn-outer",
                children=html.Button(id="import-btn", children="Importaciones", n_clicks=0),
            ),
            html.Br(),
            html.Div(
                id="export-btn-outer",
                children=html.Button(id="export-btn", children="Exportaciones", n_clicks=0),
            ),
        ],
    )
df = Data('world_trade',reporting_country='484',year=[2019],imp_exp=1).read_data()
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
                        dcc.RangeSlider(2010, 2022, value=[2021,2021], marks={
                            str(yr): str(yr) for yr in range(2010, 2022, 1)
                        },id = 'year-slider',className = 'dcc_compon'),
                            
                        dcc.Graph(id="treemap",config={'displayModeBar':True},style={'margin-top': '0px'},
                                figure=px.treemap(df,
                                path=['description','SA_4'],
                                values='tradevalue',
                                height=800, width=900))
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
                                dcc.Graph(id = 'indicator', config={'displayModeBar': False}, className='dcc_compon',
                                                    style={'margin-top': '15px'})
                                                    
                            ],)
                        ],
                    ),

                ],),
            ],
        )
    ],
)

@app.callback(Output(component_id='country_select',component_property='options'),
            Output(component_id='country_select',component_property='placeholder'),
              [Input('region_select','value')])
def paises_por_region(region_select):
    countriesList = Data('world_trade').obtaincountriesProperties(nivel=1,region=region_select)
    #countriesList = [country if len(country) < 10 else country[:10] + '...' for country in countriesList]
    placeholder = "United States of America"
    if region_select == 'North America':
        placeholder = 'United States of America'
    elif region_select == 'Asia':
        placeholder = 'China'
    elif region_select == 'Africa':
        placeholder = 'Nigeria'
    elif region_select == 'Europe':
        placeholder = 'Germany'
    elif region_select == 'Oceania':
        placeholder = 'Australia'
    return [{"label": i, "value": i} for i in countriesList], placeholder


# @app.callback(Output(component_id='country_select',component_property='value'),
#                 Input('country_select','options'),)
# def set_country_select(country_select):
#     try:
#         return country_select[0]['value']
#     except:
#         return None


# @app.callback(Output('product-select','value'),
#                 Input('product-select','options'),
#                 Input('filtro_btn','n_clicks'),)

# def set_product_select(product_select,n_clicks):
#     try:
#         if n_clicks > 0:
#             return product_select[0]['value']
#     except:
#         return None

@app.callback(Output(component_id='origen-destino',component_property='figure'),
                Output(component_id='treemap',component_property='figure'),
                Output(component_id='indicator',component_property='figure'),
                #Input('filtro_btn','n_clicks'),
                Input('region_select','value'),
                Input('country_select','value'),
                Input('product-select','value'),
                Input('year-slider','value'),
                Input('import-btn','n_clicks'),
                Input('export-btn','n_clicks'),)
def filtro(region_selected,country_select,product_select,year_slider,import_btn,export_btn):
    imp_exp = 1
    if type(country_select) == list:
        country_select = country_select[0]
    else:
        pass

    if "import-btn" == ctx.triggered_id:
        imp_exp =1
    elif "export-btn" == ctx.triggered_id:
        imp_exp = 2
    if bool(country_select):
        pais = Data('world_trade').getCountryProperties(name=country_select)
    else:
        pais = None
    c = Data('world_trade',reporting_country='484',year=year_slider,region=region_selected,partner_code=pais,imp_exp=imp_exp)
    df = c.read_data()

    fig1 = px.treemap(df,
                    path=['description','SA_4'],
                    values='tradevalue',
                    height=800, width=900).update_layout(margin=dict(t=25, r=0, l=5, b=20))

    #c = Data('world_trade_',reporting_country='484',year=year_slider,imp_exp=imp_exp,region=region_selected,partner_code=pais)
    #df2 = c.cambio_porcentualImpExp()
    df_ = df.groupby('iso_3',group_keys=False).sum().reset_index()
    imp_exp_ =0
    imp_exp_ = 'Orígenes' if imp_exp_ == 1 else 'Destinos'
    fig2 = px.choropleth(df_, locations='iso_3', 
                            color='tradevalue',
                            color_continuous_scale="viridis",
                            range_color=(df.tradevalue.min(), df.tradevalue.max()),
                            scope = region_selected.lower(),
                            #labels={'aumento_disminucion':'Aumento/disminucion'},
                            title='{imp_exp} ({año})'.format(imp_exp=imp_exp_,año=year_slider[0]),
                            projection='kavrayskiy7',
                            height = 400,
                        ).update_layout(margin={"r":0,"t":25,"l":0,"b":20}) 
    fig3 = make_subplots(rows=2, cols=3,subplot_titles=(region_selected))
    c = Data('world_trade',reporting_country='484',year=[2015,2016,2017,2018,2019,2020,2021],region=region_selected)
    df = c.read_data()
    df=df.groupby(['year','imp_exp'],group_keys=False)['tradevalue'].sum().reset_index()
    df_imp= df[df['imp_exp']==1]
    df_exp = df[df['imp_exp']==2]
    fig4 = make_subplots(rows=1, cols=1,subplot_titles=(region_selected))
    fig4.add_trace(go.Scatter(x=df_imp['year'],y=df_imp['tradevalue'],name='Importaciones',line_color='blue'),row=1,col=1)
    fig4.add_trace(go.Scatter(x=df_exp['year'],y=df_exp['tradevalue'],name='Exportaciones',line_color='green'),row=1,col=1)
    fig4.update_layout(barmode='group',height=400,margin=dict(t=25, r=0, l=5, b=20))





    # fig4=px.scatter(
    #                     x=df_imp['year'],
    #                     y=df_imp['tradevalue'],)
                        

    return fig2,fig1,fig4
# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)

