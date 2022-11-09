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
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
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
    regionsList = ['Mundo']
    regionsList_ = Data('world_trade').obtaincountriesProperties(nivel=2,region='America')
    regionsList.extend(regionsList_)
    regionsList.remove('SE')
    productsList = Data('world_trade').obtainProductoDescription(detalle=1)
    
    regionsList = [region if len(region) < 20 else region[:10] + '...' for region in regionsList]
    #productsList = [product if len(product) < 15 else product[:10] + '...' for product in productsList]

    return html.Div(
        id="control-card",
        children=[
            html.P("Selecciona una región"),
            dcc.Dropdown(
                id="region_select",
                options=[{"label": i, "value": i} for i in regionsList],
                value='América del Norte',
                #placeholder='North America',
            ),
            html.Br(),
            html.P("Selecciona un país"),
            dcc.Dropdown(
                id="country_select",
                multi=True,
            ),
            html.Br(),
            html.P("Selecciona un producto"),
            dcc.Dropdown(
                id="product-select",
                options=[{"label": i, "value": i} for i in productsList],
                #value='Todos',
                multi=True,
                placeholder="Productos minerales",
            ),
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
                        #####html.B(id='titulo'),
                        html.Div(children=[
                            html.P(id = 'titulo',style={'text-align': 'center', 'color': 'white'}),
                        ],className = 'titulo-indicador'),
                        html.Hr(),
                        html.B('Selecciona un año', className = 'fix_label', style = {'text-align': 'left', 'color': 'black'}),
                        dcc.RangeSlider(2010, 2022, value=[2020], marks={
                            str(yr): str(yr) for yr in range(2010, 2022, 1)
                        },id = 'year-slider',className = 'dcc_compon'),
                        
                        dcc.Loading(
                            id="ls-loading-2",
                            children=[html.Div([html.Div(id="ls-loading-output-2")])],
                            type="circle",
                        ),
                        dcc.Graph(id="treemap",config={'displayModeBar':True},style={'margin-top': '0px'},)
                    ],
                ),
                
                html.Div([
                    html.Div(
                        id="wait_time_card",
                        className="six columns",
                        children=[
                            #html.B("Patient Wait Time and Satisfactory Scores"),
                            html.Div(children=[
                                html.P(id='titulo-origen-destino',style={'text-align': 'center', 'color': 'white'}),
                            ],className = 'titulo-indicador'),
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
                            html.Div(children=[
                                html.P(id = 'imp-vs-exp',style={'text-align': 'center', 'color': 'white'}),
                            ],className = 'titulo-indicador'),
                            html.Div([
                                dcc.Graph(id = 'indicator', config={'displayModeBar': False}, className='dcc_compon',
                                                    style={'margin-top': '15px'})
                                                    
                            ],)
                        ],
                    ),

                ],),

                html.Div(
                    id="ventaja-competitiva-container",
                    className="twelve columns",
                    children=[
                        html.Div(children=[
                            html.P(id = 'hola',style={'text-align': 'center', 'color': 'white'}),
                        ],className = 'titulo-indicador'),
                        html.Div([
                            dcc.Graph(id = 'ventaja-competitiva', config={'displayModeBar': False}, className='dcc_compon',
                                                style={'margin-top': '15px'})
                                                
                        ],)
                    ],
                ),




            ],
        ),
        dcc.Store(id='store-df', data=[], storage_type='memory'),
        dcc.Store(id='store-imp_exp', data=[], storage_type='memory') # 'local' or 'session'),
    ],
)



@app.callback(Output("ls-loading-output-1", "children"), Input("ls-input-1", "value"))
def input_triggers_spinner(value):
    return value

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
    if selected_region == 'Mundo':
        df_inicial_ = Data('world_trade',reporting_country='484',year=[2015,2016,2017,2018,2019,2020,2021],region=selected_region).read_data()
    else:
        df_inicial_ =  Data('world_trade',reporting_country='484',year=[2015,2016,2017,2018,2019,2020,2021],region=selected_region).read_data()
    data = df_inicial_.to_json(orient='split')
    #print(df_inicial_)
    return data
   

@app.callback(Output(component_id='country_select',component_property='options'),
            #Output(component_id='country_select',component_property='value'),
              [Input('region_select','value')])
def paises_por_region(region_select):
    if region_select == 'Mundo':
        countriesList = Data('world_trade').obtaincountriesProperties(nivel=3)
    else:
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
                Input('store-imp_exp', 'data'),
                #Input('filtro-btn','n_clicks'),
                Input('region_select','value'),
                Input('country_select','value'),
                Input('product-select','value'),
                Input('year-slider','value'),
                Input('import-btn','n_clicks'),
                Input('export-btn','n_clicks'),
                )
def update_treemap(data_df,data_imp_exp,region_select,country_select,product_select,year_slider,import_btn,export_btn):
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
        df = df_inicial[(df_inicial['name'].isin(country_select))]  if len(country_select) > 0 else df 
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
                    height=500, width=900,
                    hover_data=['porcentaje'],
                    ).update_layout(margin=dict(t=25, r=0, l=5, b=20),
                    )
    return fig1



@app.callback(Output(component_id='origen-destino',component_property='figure'),
                Output(component_id='indicator',component_property='figure'),
                Output(component_id='ventaja-competitiva',component_property='figure'),
                Output('titulo', 'children'),
                Output('titulo-origen-destino', 'children'),
                Output('imp-vs-exp', 'children'),
                Input('store-df', 'data'),
                Input('store-imp_exp', 'data'),
                Input('treemap', 'clickData'),
                Input('origen-destino', 'clickData'),
                Input('region_select','value'),
                Input('country_select','value'),
                Input('product-select','value'),
                Input('year-slider','value'),
                Input('import-btn','n_clicks'),
                Input('export-btn','n_clicks'),
                )
def crear_graficas(data_df,data_imp_exp,clickData1,clickData2,selected_region,country_select,product_select,year_slider,import_btn,export_btn):
    imp_exp = data_imp_exp
    df_inicial = pd.read_json(data_df, orient='split')

    df = df_inicial.copy()
    try: #Si se selecciona un producto
        if product_select != None and len(product_select) > 0:
            df = df[df['description'].isin(product_select)]
        else:
            pass
    except:pass
        

    try: #Si hay algún país seleccionado
        df = df[(df['name'].isin(country_select))]  if len(country_select) > 0 else df 
    except:pass
        #df = df[(df['year'].isin(year_slider)) & (df['imp_exp'] == imp_exp)]
 
    if clickData1 is not None: #Si se ha dado click en algún caítulo del treemap
        try: #Si se selecciona un producto en el treemap
            if clickData1['points'][0]['id'] in df_inicial['description'].values:
                df = df[df['description'] == clickData1['points'][0]['id']]
        except:pass
    else:
        pass


    # if clickData2 is not None: #Si se ha dado click en algún país de la choropleth
    #     try:       
    #         country = clickData2['points'][0]['location']
    #         df = df_inicial[(df_inicial['iso_3']==country)]
    #     except:pass

    #Gráfica de origen-destino (chrolopleth)
    df_aux = df[(df['year'].isin(year_slider)) & (df['imp_exp'] == imp_exp)]
    df_cpleth= df_aux.groupby('iso_3',group_keys=False).sum().reset_index()
    region = selected_region
    scope_ = 'asia' if region == 'Asia' else 'africa' if region == 'Africa' else 'europe' if region == 'Europa' else 'north america' if region == 'América del Norte' else 'south america' if region == 'América del Sur' else 'oceania' if region == 'Oceanía' else 'world'
    imp_exp_ = 'Orígenes de importación en {}'.format(region) if imp_exp == 1 else 'Destinos de exportación en {}'.format(region)
    fig2 = px.choropleth(df_cpleth, locations='iso_3', 
                            color='tradevalue',
                            color_continuous_scale="viridis",
                            range_color=(df_cpleth.tradevalue.min(), df_cpleth.tradevalue.max()),
                            scope = scope_.lower(),
                            #labels={'aumento_disminucion':'Aumento/disminucion'},
                            #title='{imp_exp} ({año})'.format(imp_exp=imp_exp_,año=year_slider[0]),
                            projection='kavrayskiy7',
                            height = 400,
                        ).update_layout(margin={"r":0,"t":25,"l":5,"b":20}) 


    #Gráfica de histórico de importaciones y exportaciones (line plot)
    df_line_plot=df.groupby(['year','imp_exp'],group_keys=False)['tradevalue'].sum().reset_index()
    df_imp= df_line_plot[df_line_plot['imp_exp']==1]
    df_exp = df_line_plot[df_line_plot['imp_exp']==2]
    fig4 = make_subplots(rows=1, cols=1,) #subplot_titles=('Importación vs Exportación en {}'.format(region)
    fig4.add_trace(go.Scatter(x=df_imp['year'],y=df_imp['tradevalue'],name='Importaciones',line_color='blue'),row=1,col=1)
    fig4.add_trace(go.Scatter(x=df_exp['year'],y=df_exp['tradevalue'],name='Exportaciones',line_color='green'),row=1,col=1)
    fig4.update_layout(barmode='group',height=400,margin=dict(t=25, r=0, l=5, b=20),
                        legend=dict(
                        yanchor="bottom",
                        y=0.85,
                        xanchor="left",
                        x=0.02))

    #Gráfica relación importación-exportación de productos (bubble chart)
    df_bubble_chart = df_inicial.copy()
    if clickData2 is not None:
        try: #Si se selecciona un producto en el treemap
            print(clickData2['points'][0]['location'])
            country = clickData2['points'][0]['location']
            df_aux2 = df_inicial[(df_inicial['year'].isin(year_slider)) & (df_inicial['iso_3']==country)]
            df_bubble_chart = df_aux2.groupby(['year','imp_exp','description','SA_4'])['tradevalue'].sum().reset_index()
            df_imp = df_bubble_chart[df_bubble_chart['imp_exp'] == 1]
            df_imp.drop(columns=['imp_exp','year'],inplace=True)
            df_exp = df_bubble_chart[df_bubble_chart['imp_exp'] == 2]
            df_exp.drop(columns=['imp_exp','year'],inplace=True)
            #juntar los dos dataframes con SA_4 como clave primaria
            df_bubble_chart = pd.merge(df_exp,df_imp,on=['SA_4','description'],how='outer')
            df_bubble_chart.rename(columns={'tradevalue_x':'export','tradevalue_y':'import'},inplace=True)
            df_bubble_chart['export'] = df_bubble_chart['export'].apply(lambda x:0 if np.isnan(x) else x)
            df_bubble_chart['import'] = df_bubble_chart['import'].apply(lambda x:0 if np.isnan(x) else x)
            #crear una columna con el dato mayor 
            df_bubble_chart['max'] = df_bubble_chart[['export','import']].max(axis=1)

        except Exception as e:
            print(e)
            return dash.no_update
    try:
        fig5 = px.scatter(df_bubble_chart, x="export", y="import", size="max", color="description", hover_name="SA_4", log_x=True,log_y=True, size_max=60,hover_data={'SA_4':True,'description':True,'max':False})
        #ajustar xaxis y yaxis en función de minimo y del máximo de los valores de export e import
        #sacar el quantile 25 de importacion y exportacion
        min_export_ = df_bubble_chart['export'].quantile(0.25)
        min_import_ = df_bubble_chart['import'].quantile(0.25)
        min_export = np.log10(min_export_)
        min_import= np.log10(min_import_)   
          
        max_import_ = df_bubble_chart['import'].max()
        max_export_= df_bubble_chart['export'].max()
        max_export = np.log10(max_export_)
        max_import = np.log10(max_import_)

        fig5.update_layout(xaxis_range=[min_export,max_export+0.3],yaxis_range=[min_import, max_import+0.3],height=400,width=900,margin=dict(t=25, r=0, l=5, b=20),showlegend=True)
        #agregar una pendiente de 45° que tome en cuente la escala logaritmica
        fig5.add_trace(go.Scatter(x=[min_export_, max_export_+1000], y=[min_import_, max_import_+1000],mode='lines',line=dict(color='black', width=1, dash='dash')))
    except Exception as e:
        print(e)    
        fig5 = px.line(x=[1,2,3],y=[1,2,3])

    #Regresa el título de las gráficas
    imp_exp_ = 1 if imp_exp == 1 else 2
    if imp_exp_ == 1:
        titulo = 'Importaciones a México desde {} ({})'.format(selected_region,year_slider[0])
        titulo_origen_destino_graph = 'Orígenes de importación ({})'.format(year_slider[0])
         
    else:
        titulo = 'Exportaciones de México hacia {} ({})'.format(selected_region,year_slider[0])
        titulo_origen_destino_graph = 'Destinos de exportación ({})'.format(year_slider[0])

    titulo_imp_exp = 'Importación vs Exportación (2015-2021)'.format(year_slider[0])

    return fig2,fig4,fig5,titulo,titulo_origen_destino_graph,titulo_imp_exp



# @app.callback(Output(component_id='ventaja-competitiva',component_property='figure'),
#                 Input('store-df', 'data'),
#                 Input('origen-destino', 'clickData'),
#                 Input('year-slider','value'),
#                 )


# def crear_grafica_ventaja_competitiva(data_df,clickData2,year_slider):
#     df_inicial = pd.read_json(data_df, orient='split')
#     print(df_inicial.columns)

#     return fig5
    
        
# Run the server
if __name__ == "__main__":
    app.run_server(debug=True)
