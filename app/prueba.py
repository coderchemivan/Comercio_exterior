import dash
from dash import Dash, html, Input, Output, State,ctx,dcc,callback
from dash.dependencies import Input, Output, ClientsideFunction
import dash_daq as daq
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd 
import math

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
    regionsList = Data('world_trade',fuente_datos='csv').obtaincountriesProperties(nivel=2,region='America')
    regionsList.remove('SE')
    regionsList = [region if len(region) < 20 else region[:10] + '...' for region in regionsList]
    #productsList = [product if len(product) < 15 else product[:10] + '...' for product in productsList]

    return [
                        html.Div(
                                    className="three columns",
                                ),  
                        html.Div(
                                className="three columns",
                                children=[
                                                dcc.Dropdown(
                                                            id="region_select",
                                                            options=[{"label": i, "value": i} for i in regionsList],
                                                            value='Mundo',
                                                            placeholder='Mundo',
                                                            ),

                                        ]
                                ),
                        html.Div(
                                className="three columns",
                                children=[
                                                dcc.Dropdown(
                                                            id="country_select",
                                                            options=[{"label": i, "value": i} for i in range(10)],
                                                            placeholder='Selecciona un país',
                                                            ),

                                        ]
                                ),
                        html.Div(
                                className="two columns",
                                children=[
                                            daq.ToggleSwitch(
                                                id='imp-exp-toggle-switch',
                                                label='Exportaciones|Importaciones',
                                                labelPosition='top',
                                                value=True,

                                            )

                                        ]
                                ),
    ]
app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Div(
                    className="three columns",
                    children =[html.Img(src=app.get_asset_url("International-trade.png"))]),
                html.Div(
                        className="nine columns",
                        ),
                    ]
        ),
        html.Div(
            id="filters",
            className="filters",
            children=generate_control_card(),        
        ),
        # Left column
        html.Div(
            id="left-column",
            className="three columns",
            children=[
                
                html.Div([
                        dcc.Graph(id = 'indicador1', config={'displayModeBar': False}, className='dcc_compon',
                                style={'margin-top': '20px'}),                   
                            ]),
                html.Br(),
                html.Div([
                        dcc.Graph(id = 'indicador2', config={'displayModeBar': False}, className='dcc_compon',
                                style={'margin-top': '20px'}),                   
                            ]),
                html.Div([
                        dcc.Graph(id = 'indicador3', config={'displayModeBar': False}, className='dcc_compon',
                                style={'margin-top': '20px'}),                   
                            ]),               
            ]
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                html.Div(
                    id="control-year-slider",
                    children=[
                        html.Hr(),
                        html.Br(),
                        html.B('Selecciona un año', className = 'fix_label'),
                        dcc.RangeSlider(2014, 2022, value=[2021], 
                            marks={str(yr) : {'label' : str(yr), 'style':{'color':'white'}} for yr in range(2014, 2022,1)},
                        id = 'year-slider',className = 'slider'),
                    ],
                ),    
                html.Div(
                    children=[
                        html.Br()
                    ],
                ),            
                html.Div(
                    id="treemap-container",
                    className="pretty_container",
                    children=[
                        html.Div(children=[
                            html.P(id = 'titulo',style={'text-align': 'center', 'color': 'white'}),
                        ],className = 'titulo-grafica'),
                        dcc.Graph(id="treemap",config={'displayModeBar':True},style={'margin-top': '0px'},className='dcc_compon',)
                    ],
                ),
                
                html.Div([
                    html.Div(
                        id="wait_time_card",
                        className="six columns",
                        children=[
                            #html.B("Patient Wait Time and Satisfactory Scores"),
                            html.Div(children=[
                                html.P(id='titulo-imp-exp-pais',style={'text-align': 'center', 'color': 'black'}),
                            ],className = 'titulo-grafica'),
                            html.Div([
                                dcc.Graph(id = 'imp-exp-pais',  config={'displayModeBar': False}, className='dcc_compon',
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
                                html.P(id = 'titulo-imp-exp-producto',style={'text-align': 'center', 'color': 'white'}),
                            ],className = 'titulo-grafica'),
                            html.Div([
                                dcc.Graph(id = 'imp-exp-producto', config={'displayModeBar': False}, className='dcc_compon',
                                                    style={'margin-top': '15px'})
                                                    
                            ],)
                        ],
                    ),

                ],),

                html.Div([
                    html.Div(
                        id="imp-exp-historico-container",
                        className="twelve columns",
                        children=[
                            html.Div(children=[
                                html.P(id = 'imp-exp-historico-title',style={'text-align': 'center', 'color': 'white'}),
                            ],className = 'titulo-grafica'),
                            html.Div([
                                dcc.Graph(id = 'imp-exp-historico', config={'displayModeBar': False}, className='dcc_compon',
                                                    style={'margin-top': '15px'})
                                                    
                            ],)
                        ],
                    ),
                ],),

                html.Div([
                    html.Div(
                        id="products-distribution-container",
                        className="twelve columns",
                        children=[
                            html.Div(children=[
                                html.P(id = 'products-distribution-container-title',style={'text-align': 'center', 'color': 'white'}),
                            ],className = 'titulo-grafica'),
                            html.Div([
                                dcc.Graph(id = 'products-distribution-plot', config={'displayModeBar': False}, className='dcc_compon',
                                                    style={'margin-top': '15px'})
                                                    
                            ],)
                        ],
                    ),
                ],),

            ],
        ),
        dcc.Store(id='store-df', data=[], storage_type='memory'),
        dcc.Store(id='store-graphs_selections', data={}, storage_type='memory'),
    ],
)

@app.callback(
    Output('store-graphs_selections', 'data'),
    Input('imp-exp-toggle-switch', 'value'),
    Input('region_select', 'value'),
    Input('imp-exp-pais', 'clickData'),)
def define_imp_exp(imp_exp_,region_selected,clickCP_status):
    imp_exp = 1 if imp_exp_ else 2
    data = {}
    data['clickDataCP']=True if clickCP_status is not None else True
    data['imp_exp'] = imp_exp 
    return data
    
@app.callback(
    Output('store-df', 'data'),
    [Input('region_select', 'value')])
def store_data(selected_region):
    if selected_region !='Mundo':
        df_inicial_ = Data('world_trade',fuente_datos='csv',year=[2015,2016,2017,2018,2019,2020,2021],region=selected_region).read_data()
    else:
        df_inicial_ = Data('world_trade',fuente_datos='csv',year=[2015,2016,2017,2018,2019,2020,2021]).read_data()
    data = df_inicial_.to_json(orient='split')
    return data
   

@app.callback(Output(component_id='country_select',component_property='options'),
            #Output(component_id='country_select',component_property='value'),
              [Input('region_select','value')])
def paises_por_region(region_select):
    if region_select == 'Mundo':
        countriesList = Data('world_trade',fuente_datos='csv').obtaincountriesProperties(nivel=3)
    else:
        countriesList = Data('world_trade',fuente_datos='csv').obtaincountriesProperties(nivel=1,region=region_select)
    try:
        countriesList.remove('Mexico')
        remove_items = ['World','Antarctica']
        for item in remove_items:
            if item in countriesList:
                countriesList.remove(item)
    except:pass
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
                Input('store-graphs_selections', 'data'),
                Input('imp-exp-pais', 'clickData'),
                Input('region_select','value'),
                Input('country_select','value'),
                #Input('product-select','value'),
                Input('year-slider','value'),
                )
def update_treemap(data_df,data_graphs_settings,clickData1,region_select,country_select,year_slider):
    df_inicial = pd.read_json(data_df, orient='split')
    if region_select !='Mundo':
        df_inicial_ = df_inicial[df_inicial['region']==region_select]
    imp_exp = data_graphs_settings['imp_exp']
    df = df_inicial.copy()
    try: #Si hay algún país seleccionado
        df = df[(df['name']==country_select)]  if country_select!=None else df 
    except:pass 
    if clickData1 is not None and data_graphs_settings['clickDataCP'] == True and region_select!='Mundo': #"SI SE SELECCIONA UN PAIS EN EL MAPA"
        country = clickData1['points'][0]['location']
        #verificar que country este el df
        if country in df['iso_3'].unique():
            df_aux=df[(df['iso_3']==country)]
        else: 
            df_aux=df.copy()
        df_aux = df_aux[(df_aux['year'] ==math.floor(year_slider[0])) & (df_aux['imp_exp'] == imp_exp)]
    else:
        df_aux = df[(df['year']==math.floor(year_slider[0])) & (df['imp_exp'] == imp_exp)]
    df_treemap = df_aux.groupby(['description','SA_4','year','sa4_description'])['tradevalue','porcentaje'].sum().reset_index()
    df_treemap['porcentaje'] = df_treemap['tradevalue'].apply(lambda x:(x/df_treemap['tradevalue'].sum())*100)
    df_treemap['porcentaje'] = df_treemap['porcentaje'].apply(lambda x:round(x,2))
    df_treemap['porcentaje'] = df_treemap['porcentaje'].apply(lambda x:str(x)+'%')
    fig1 = px.treemap(df_treemap,
                    path=['description','sa4_description'],
                    values='tradevalue',
                    height=500, width=950,
                    hover_data=['porcentaje'],
                    ).update_layout(margin=dict(t=25, r=0, l=5, b=20))
    return fig1



@app.callback(Output(component_id='imp-exp-pais',component_property='figure'),
                Output(component_id='imp-exp-producto',component_property='figure'),
                Output(component_id='imp-exp-historico',component_property='figure'),
                Output('titulo', 'children'),
                Output('titulo-imp-exp-pais', 'children'),
                Output('titulo-imp-exp-producto', 'children'),
                Output('imp-exp-historico-title', 'children'),
                Output('indicador1','figure'),
                Output('indicador2','figure'),
                Output('indicador3','figure'),
                Input('store-df', 'data'),
                Input('store-graphs_selections', 'data'),
                Input('treemap', 'clickData'),
                Input('imp-exp-pais', 'clickData'),
                Input('region_select','value'),
                Input('country_select','value'),
                #Input('product-select','value'),
                Input('year-slider','value'),
                )
def crear_graficas(data_df,data_graphs_settings,clickData1,clickData2,selected_region,country_select,year_slider):
    imp_exp = data_graphs_settings['imp_exp']
    df_inicial = pd.read_json(data_df, orient='split')
    df = df_inicial.copy()        
    try: #Si hay algún país seleccionado
        df = df[(df['name']==country_select)]  if country_select!=None else df
    except Exception as e: print(e)
        #df = df[(df['year'].isin(year_slider)) & (df['imp_exp'] == imp_exp)]
    column = 'description'
    df_aux = df
    section = ''
    if clickData1 is not None:
        #Si se ha dado click en algún capítulo del treemap
        try: 
            id = clickData1['points'][0]['id'].split('/')[1] if clickData1['points'][0]['currentPath']!= '/' else clickData1['points'][0]['id'].split('/')[0]
            section = id
            column = 'sa4_description'
            column_filtro = 'sa4_description' if clickData1['points'][0]['currentPath']!= '/' else 'description'
            if id.strip() in df_inicial['{}'.format(column_filtro)].values:
                df_aux = df[df['{}'.format(column_filtro)] == id.strip()]
        except:pass
    else:
        pass


    #gráfica importaciones/exportaciones por país
    selected_year = math.floor(year_slider[0])
    df_var_pais = Data().cambio_porcentualImpExp(df_aux,pais_producto='pais',lista_columnas=['year','imp_exp','partner_code','iso_3','name'],columna='partner_code',year=selected_year,imp_exp=imp_exp)
    fig1 = px.bar(df_var_pais,
                x='tradevalue',
                y='iso_3',
                orientation='h',
                color_discrete_sequence=px.colors.qualitative.Dark24,
                height=400,
                text_auto='.2s',
                #color verde si aumento, rojo si disminuyo
                color='aumento_disminucion',
                color_continuous_scale=['red','green'],
                range_color=(-50, 50),
                #mostrar columna porcentaje en tooltip
                ).update_layout(margin=dict(t=25, r=0, l=5, b=20),xaxis={'visible':False},showlegend=False,coloraxis_showscale=False,
                yaxis= {'anchor': 'x', 'domain': [0.0, 1.0], 'title': {'text': ''}})
    fig1.update_traces(textfont_size=12, textangle=0, textposition="inside", cliponaxis=False)
    

    #gráfica importaciones/exportaciones por producto
    df_var_producto = Data().cambio_porcentualImpExp(df_aux,pais_producto='producto',lista_columnas=['year','imp_exp',column],columna=column,year=selected_year,imp_exp=imp_exp)
    fig2 = px.bar(df_var_producto,
                x='tradevalue',
                y=column,
                orientation='h',
                color_discrete_sequence=px.colors.qualitative.Dark24,
                height=400,
                text_auto='.2s',
                #color verde si aumento, rojo si disminuyo
                color='aumento_disminucion',
                color_continuous_scale=['red','green'],
                range_color=(-50, 50),
                #mostrar columna porcentaje en tooltip
                ).update_layout(margin=dict(t=25, r=0, l=5, b=20),xaxis={'visible':False},showlegend=False,coloraxis_showscale=False
                ,yaxis= {'anchor': 'x', 'domain': [0.0, 1.0], 'title': {'text': ''}})
    fig2.update_traces(textfont_size=12, textangle=0, textposition="inside", cliponaxis=False)

    



    #Gráfica de histórico de importaciones y exportaciones (line plot)
    df_line_plot=df_aux.groupby(['year','imp_exp'],group_keys=False)['tradevalue'].sum().reset_index()
    df_imp= df_line_plot[df_line_plot['imp_exp']==1]
    df_exp = df_line_plot[df_line_plot['imp_exp']==2]
    fig3 = make_subplots(rows=1, cols=1,) #subplot_titles=('Importación vs Exportación en {}'.format(region)
    fig3.add_trace(go.Scatter(x=df_imp['year'],y=df_imp['tradevalue'],name='Importaciones',line_color='blue'),row=1,col=1)
    fig3.add_trace(go.Scatter(x=df_exp['year'],y=df_exp['tradevalue'],name='Exportaciones',line_color='green'),row=1,col=1)
    fig3.update_layout(barmode='group',height=400,margin=dict(t=25, r=0, l=5, b=20),
                        legend=dict(
                        yanchor="bottom",
                        y=0.85,
                        xanchor="left",
                        x=0.02))


    imp_exp_ = 'Importaciones' if imp_exp == 1 else 'Exportaciones'
    try:
        region = country_select if country_select!=None else selected_region 
    except:
        region = selected_region 

    #titulos de las gráficas
    titulo_treemap = '{} a México desde {} ({})'.format(imp_exp_,region,math.floor(year_slider[0]))
    titulo_origen_destino_país = '{} por país ({})'.format(imp_exp_,math.floor(year_slider[0]))
    titulo_origen_destino_producto = '{} por producto ({})'.format(imp_exp_,math.floor(year_slider[0]))
    titulo_imp_exp_historico = 'Importación vs Exportación (2015-2021)'.format(math.floor(year_slider[0]))


    totales = df_aux.groupby(['year','imp_exp'],group_keys=False)['tradevalue'].sum().reset_index()
    total_imp_exp_years = totales[(totales['year'].isin([math.floor(year_slider[0]),math.floor(year_slider[0])-1])) 
                                                        & (totales['imp_exp']==imp_exp)]

    

    
    df_var_pais = df_var_pais[['name','tradevalue','aumento_disminucion']].sort_values(by='aumento_disminucion',ascending=False).head(3)
    df_var_pais['tradevalue_año_anterior'] = df_var_pais['tradevalue'] - df_var_pais['tradevalue']*df_var_pais['aumento_disminucion']/100
    df_var_pais = df_var_pais.to_dict('records')
    
    df_var_producto = df
    if section in df_inicial['description'].values:
        df_var_producto = df_var_producto[df_var_producto['description'] == section]
    df_var_producto = Data().cambio_porcentualImpExp(df_var_producto,pais_producto='producto',lista_columnas=['year','imp_exp','sa4_description'],columna='sa4_description',year=selected_year,imp_exp=imp_exp)
    df_var_producto = df_var_producto[['sa4_description','tradevalue','aumento_disminucion']].sort_values(by='aumento_disminucion',ascending=False).head(3)
    df_var_producto['tradevalue_año_anterior'] = df_var_producto['tradevalue'] - df_var_producto['tradevalue']*df_var_producto['aumento_disminucion']/100
    df_var_producto = df_var_producto.to_dict('records')

    indicator1 = go.Figure()
    indicator1.add_trace(go.Indicator(
                mode = "number+delta",
                value = total_imp_exp_years['tradevalue'].iloc[1],
                title= {'text': 'Total de {}'.format(imp_exp_.lower()),'font': {'size': 25}},
                #value format en millones
                number={'valueformat': ".2s",'font': {'size': 25}},
                delta = {'reference': total_imp_exp_years['tradevalue'].iloc[0], 'relative': True,'valueformat': '.1%','font': {'size': 20},'position': "right"},
                domain = {'x': [0, 1], 'y': [0, 1]}))
    indicator1.update_layout(
            title={
                   'y': 1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='black',size=25),
            paper_bgcolor='#e5ecf6',
            plot_bgcolor='#e5ecf6',
            height = 200)

    indicator2 = go.Figure()
    
    indicator2.add_trace(go.Indicator(
            mode = "number+delta",
            value = df_var_pais[0]['tradevalue'],
            title = {'text': df_var_pais[0]['name'],'font': {'size': 30}},
            #value format en millones
            number={'valueformat': ".2s",'font': {'size': 25}},
            #dar formato a delta en % con cero decimales
            delta = {'reference': df_var_pais[0]['tradevalue_año_anterior'], 'relative': True,'valueformat': '.1%','font': {'size': 20},'position': "right"},
            domain = {'x': [0, 1], 'y': [0, 1]}),
            )
    indicator2.update_layout(
            title={'text': 'Mercado de mayor crecimiento',
                   'y': 0.9,    
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='black'),
            paper_bgcolor='#e5ecf6',
            plot_bgcolor='#e5ecf6',
            height = 200)


    indicator3 = go.Figure()
    
    indicator3.add_trace(go.Indicator(
            mode = "number+delta",
            value = df_var_producto[0]['tradevalue'],
            title = {'text':df_var_producto[0]['sa4_description'],'font': {'size': 30}},
            #value format en millones
            number={'valueformat': ".2s",'font': {'size': 25}},
            delta = {'reference': df_var_producto[0]['tradevalue_año_anterior'], 'relative': True,'valueformat': '.1%','font': {'size': 20},'position': "right"},
            domain = {'x': [0, 1], 'y': [0, 1]}),
            )
    indicator3.update_layout(
            title={'text': 'Mercado de mayor crecimiento',
                   'y': 0.9,    
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color='black'),
            paper_bgcolor='#e5ecf6',
            plot_bgcolor='#e5ecf6',
            height = 200)

    return fig1,fig2,fig3,titulo_treemap,titulo_origen_destino_país,titulo_origen_destino_producto,titulo_imp_exp_historico,indicator1,indicator2,indicator3
# # Run the server
if __name__ == "__main__":
    app.run_server(debug=True)



# sankey 
# slope
# waterfull
# ribbon chart