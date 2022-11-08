import dash
from dash import Dash, html, Input, Output, State,ctx,dcc,callback
from dash.dependencies import Input, Output, ClientsideFunction
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd 


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

def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Comercio internacional"),
            #html.H3("Welcome to the Clinical Analytics Dashboard"),
            html.Div(
                id="intro",
                children="Explora el mercado internacional de México con el mundo",
            ),
        ],
    )


def generate_control_card():
    """:return: A Div containing controls for graphs.
    """
    
    regionsList = Data('world_trade').obtaincountriesProperties(nivel=2,region='America')
    productsList = Data('world_trade').obtainProductoDescription(detalle=4)
    
    regionsList = [region if len(region) < 20 else region[:10] + '...' for region in regionsList]
    #productsList = [product if len(product) < 15 else product[:10] + '...' for product in productsList]

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
                #value=["United States of America",'Canada'],
                multi=True,
                placeholder="United States of America",
            ),
            html.Br(),
            html.P("Select a product"),
            dcc.Dropdown(
                id="product-select",
                options=[{"label": i, "value": i} for i in productsList],
                #value='Todos',
                multi=True,
                placeholder="Crudo",
            ),
            # html.Br(),
            # html.P("Indicator"),
            # dcc.Dropdown(
            #     id="indicador-select",
            #     options={'linea de tiempo': 'Linea de tiempo', 'crecimiento': 'Crecimiento'},
            #     #value='Animales vivos',
            #     multi=False,
            #     placeholder="Crudo",
            # ),
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
            html.Br(),
            html.Div(
                id="filtro-btn-outer",
                children=html.Button(id="filtro-btn", children="Crear visualización", n_clicks=0),
            ),
        ],
    )
#df = Data('world_trade',reporting_country='484',year=[2019],imp_exp=1).read_data()
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
            children=[description_card(),generate_control_card()]
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
                        html.B(id='titulo'),
                        html.Hr(),
                        html.B('Selecciona un año', className = 'fix_label', style = {'text-align': 'left', 'color': 'black'}),
                        dcc.RangeSlider(2010, 2022, value=[2020], marks={
                            str(yr): str(yr) for yr in range(2010, 2022, 1)
                        },id = 'year-slider',className = 'dcc_compon'),
                            
                        dcc.Graph(id="treemap",config={'displayModeBar':True},style={'margin-top': '0px'},)
                                #figure=px.treemap(df,
                                #path=['description','SA_4'],
                                #values='tradevalue',
                                #height=800, width=900))
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

                html.Div(
                    id="testing_graph",
                    children=[
                        html.Hr(),
                        html.B('Selecciona un año', className = 'fix_label', style = {'text-align': 'left', 'color': 'black'}),                            
                        dcc.Graph(id="treemap2",config={'displayModeBar':True},style={'margin-top': '0px'},)
                    ],
                ),




            ],
        ),
        dcc.Store(id='store-df', data=[], storage_type='memory'),
        dcc.Store(id='store-imp_exp', data=[], storage_type='memory') # 'local' or 'session'),
    ],
)

@app.callback(
    Output('store-imp_exp', 'data'),
    [Input('import-btn', 'n_clicks'),
    Input('export-btn', 'n_clicks')],)
def define_imp_exp(n_clicks_imp,n_clicks_exp):
    imp_exp=1
    if "import-btn" == ctx.triggered_id:
        imp_exp =1
    elif "export-btn" == ctx.triggered_id:
        imp_exp = 2
    data = imp_exp
    return data
    
@app.callback(
    Output('store-df', 'data'),
    [Input('region_select', 'value')])
def store_data(selected_region):
    c = Data('world_trade',reporting_country='484',year=[2015,2016,2017,2018,2019,2020,2021],region=selected_region)
    df_inicial_ = c.read_data()
    data = df_inicial_.to_json(orient='split')
    return data
   

@app.callback(Output(component_id='country_select',component_property='options'),
            #Output(component_id='country_select',component_property='value'),
              [Input('region_select','value')])
def paises_por_region(region_select):
    countriesList = Data('world_trade').obtaincountriesProperties(nivel=1,region=region_select)
    #countriesList = [country if len(country) < 10 else country[:10] + '...' for country in countriesList]
    #placeholder = "United States of America"
    # if region_select == 'North America':
    #     value = ['United States of America','Canada']
    # elif region_select == 'Asia':
    #     value = ['China','Japan','South Korea','India']
    # elif region_select == 'Africa':
    #     value = ['Nigeria']
    # elif region_select == 'Europe':
    #     value = ['Germany','Spain','France']
    # elif region_select == 'Oceania':
    #     value = 'Australia'
    # elif region_select == 'South America':
    #     value = ['Brazil','Argentina','Chile','Colombia','Peru']
    return [{"label": i, "value": i} for i in countriesList]



@app.callback(Output(component_id='treemap',component_property='figure'),
                Input('store-df', 'data'),
                State('store-imp_exp', 'data'),
                Input('filtro-btn','n_clicks'),
                Input('region_select','value'),
                Input('country_select','value'),
                Input('product-select','value'),
                Input('year-slider','value'),
                Input('import-btn','n_clicks'),
                Input('export-btn','n_clicks'),
                )
def update_treemap(data_df,data_imp_exp,n_clicks,region_select,country_select,product_select,year_slider,import_btn,export_btn):
    imp_exp = data_imp_exp
    df_inicial = pd.read_json(data_df, orient='split')

    df = df_inicial.copy()
    try: #Si se selecciona un producto
        if product_select != None and len(product_select) > 0:
            df = df[df['description'].isin(product_select)]
        else:
            df = df_inicial.copy()
    except:pass
        

    try: #Si hay algún país seleccionado
        df = df[(df['name'].isin(country_select))]  if len(country_select) > 0 else df 
    except:pass
        #df = df[(df['year'].isin(year_slider)) & (df['imp_exp'] == imp_exp)]
 
    df_aux = df[(df['year'].isin(year_slider)) & (df['imp_exp'] == imp_exp)]
    df_treemap = df_aux.groupby(['description','SA_4','year','sa4_description'])['tradevalue','porcentaje'].sum().reset_index()
    df_treemap['porcentaje'] = df_treemap['tradevalue'].apply(lambda x:(x/df_treemap['tradevalue'].sum())*100)
    df_treemap['porcentaje'] = df_treemap['porcentaje'].apply(lambda x:round(x,2))
    df_treemap['porcentaje'] = df_treemap['porcentaje'].apply(lambda x:str(x)+'%')
    fig1 = px.treemap(df_treemap,
                    path=['description','sa4_description'],
                    values='tradevalue',
                    height=800, width=900,
                    hover_data=['porcentaje'],
                    ).update_layout(margin=dict(t=25, r=0, l=5, b=20),
                    )
    return fig1







@app.callback(Output(component_id='origen-destino',component_property='figure'),
                Output(component_id='indicator',component_property='figure'),
                Output('titulo', 'children'),
                Input('store-df', 'data'),
                State('store-imp_exp', 'data'),
                Input('treemap', 'clickData'),
                Input('filtro-btn','n_clicks'),
                Input('region_select','value'),
                Input('country_select','value'),
                Input('product-select','value'),
                Input('year-slider','value'),
                Input('import-btn','n_clicks'),
                Input('export-btn','n_clicks'),
                )
def crear_graficas(data_df,data_imp_exp,clickData,n_clicks,selected_region,country_select,product_select,year_slider,import_btn,export_btn):
    imp_exp = data_imp_exp
    df_inicial = pd.read_json(data_df, orient='split')

    df = df_inicial.copy()
    try: #Si se selecciona un producto
        if product_select != None and len(product_select) > 0:
            df = df[df['description'].isin(product_select)]
        else:
            df = df_inicial.copy()
    except:pass
        

    try: #Si hay algún país seleccionado
        df = df[(df['name'].isin(country_select))]  if len(country_select) > 0 else df 
    except:pass
        #df = df[(df['year'].isin(year_slider)) & (df['imp_exp'] == imp_exp)]
 
    if clickData is not None: #Si se selecciona un producto en el treemap
        if clickData['points'][0]['id'] in df_inicial['description'].values:
            df = df[df['description'] == clickData['points'][0]['id']]
    else:
        pass

    df_aux = df[(df['year'].isin(year_slider)) & (df['imp_exp'] == imp_exp)]
    df_cpleth= df_aux.groupby('iso_3',group_keys=False).sum().reset_index()
    region = selected_region
    imp_exp_ = 'Orígenes de importación en {}'.format(region) if imp_exp == 1 else 'Destinos de exportación en {}'.format(region)
    fig2 = px.choropleth(df_cpleth, locations='iso_3', 
                            color='tradevalue',
                            color_continuous_scale="viridis",
                            range_color=(df_cpleth.tradevalue.min(), df_cpleth.tradevalue.max()),
                            scope = selected_region.lower(),
                            #labels={'aumento_disminucion':'Aumento/disminucion'},
                            title='{imp_exp} ({año})'.format(imp_exp=imp_exp_,año=year_slider[0]),
                            projection='kavrayskiy7',
                            height = 400,
                        ).update_layout(margin={"r":0,"t":25,"l":0,"b":20}) 

    df_line_plot=df.groupby(['year','imp_exp'],group_keys=False)['tradevalue'].sum().reset_index()
    df_imp= df_line_plot[df_line_plot['imp_exp']==1]
    df_exp = df_line_plot[df_line_plot['imp_exp']==2]
    fig4 = make_subplots(rows=1, cols=1,subplot_titles=('Importación vs Exportación en {}'.format(region),))
    fig4.add_trace(go.Scatter(x=df_imp['year'],y=df_imp['tradevalue'],name='Importaciones',line_color='blue'),row=1,col=1)
    fig4.add_trace(go.Scatter(x=df_exp['year'],y=df_exp['tradevalue'],name='Exportaciones',line_color='green'),row=1,col=1)
    fig4.update_layout(barmode='group',height=400,margin=dict(t=25, r=0, l=5, b=20))
    imp_exp_ = 1 if imp_exp == 1 else 2
    if imp_exp_ == 1:
        titulo = 'Importaciones a México en el año {}'.format(year_slider[0])
         
    else:
        titulo = 'Exportaciones de México en el año {}'.format(year_slider[0])


 
    return fig2,fig4,titulo

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)

