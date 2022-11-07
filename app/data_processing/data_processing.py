import pandas as pd
import numpy as np
import mysql.connector 
import plotly.express as px
import json
from plotly.subplots import make_subplots
import plotly.graph_objects as go
class Data():
    def __init__(self,table_name=None,reporting_country=None,region=None,partner_code = None,year=None,period=None,section=None,SA_4=None,imp_exp=None):
        self.conn = mysql.connector.connect(user="root", password="123456",
                                       host="localhost",
                                       database="mexico_it",
                                       port='3306'
                                       )
        self.table_name = table_name
        self.reporting_country = reporting_country
        self.region = region
        self.partner_code = partner_code
        self.year = year
        self.period = period
        self.section = section
        self.SA_4 = SA_4
        self.imp_exp = imp_exp



    def read_data(self):
        #diccionario con los parametros de la consulta
        diccionario_filtro = {'reporter_country':self.reporting_country,
                                'partner_code':self.partner_code,
                                'year':self.year,
                                'period':self.period,
                                'section':self.section,
                                'SA_4':self.SA_4,
                                'imp_exp':self.imp_exp}

        #parametros de la consulta que ingresó el usuario
        diccionario_filtro = {k: v for k, v in diccionario_filtro.items() if v is not None}
        line_ =''
        for k,v in diccionario_filtro.items():
            line_ = ''.join('{} in ({}) AND '.format(k, str(v).replace('[','').replace(']','')) for k, v in diccionario_filtro.items())[0:-4]
        
        #procesando table world_table
        if diccionario_filtro!= {}:
            query = "SELECT * FROM {} WHERE {}".format(self.table_name,line_)
        else:
            query = "SELECT * FROM {}".format(self.table_name)
        world_tradeTable = self.get_table(query)
        world_tradeTable['section'] = world_tradeTable['section'].astype(int)
        world_tradeTable = world_tradeTable[~(world_tradeTable['partner_code']=='0')] 
        world_tradeTable['porcentaje'] = world_tradeTable.groupby(['year','imp_exp','SA_4'],group_keys=False)['tradevalue'].apply(lambda x: (x/(x.sum()))*100)
        world_tradeTable['porcentaje'] = world_tradeTable['porcentaje'].round(2) 
        world_tradeTable['tradevalue'] = world_tradeTable['tradevalue'].apply(lambda x: x/1000)
        world_tradeTable = world_tradeTable[world_tradeTable['porcentaje'] > 3] 

        #procesando table sa4_description
        query = "SELECT * FROM sections"
        sectionsTable = self.get_table(query)
        sectionsTable = sectionsTable.rename(columns={'id':'section'})

        #PROCESANDO TABLA COUNTRIES_
        query = "SELECT * FROM countries_"
        countriesTable_ = self.get_table(query)
        countriesTable_ = countriesTable_.rename(columns={'id':'partner_code'})
        
        #procesando table countries
        query = "SELECT * FROM countries"
        countriesTable = self.get_table(query)  
        countriesTable = countriesTable.rename(columns={'partner_code_':'partner_code'})
        countriesTable['partner_code'] = countriesTable['partner_code'].astype(str)
        df = world_tradeTable.merge(sectionsTable,how='left',on='section')
        df = df.merge(countriesTable,how='left',on='partner_code')
        df.drop(columns=['fobvalue','quantity_unit','netweight','reporter_country','tradequantity'],inplace=True)
        #dar formato a tradevalue en millones de dolares
        df['tradevalue'] = df['tradevalue'].astype(float)
        #df['tradevalue'] = df['tradevalue'].apply(lambda x:x)
        #redondear a 2 decimales
        df['tradevalue'] = df['tradevalue'].round(2)
        #eliminar registros con tradevalue < 0
        df = df[df['tradevalue'] > 0]
        
        df = df[df['region'] == self.region]
        #print(df.shape)
        return df

    def get_table(self,query):
        cur = self.conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        table = pd.DataFrame(rows,columns=[x[0] for x in cur.description])
        cur.close()
        return table 
        
    def obtaincountriesProperties(self,nivel=1,region='Todos'):
        query = "SELECT * FROM countries"
        df = self.get_table(query)
        if nivel == 1 and region != 'Todos':
            zone_list = df[df['region']==region]['name'].values.tolist()
        elif nivel==2 and region != 'Todos':
            zone_list = df['region'].unique()
        else:
            zone_list = df['name'].values.tolist()
        return zone_list
    def getCountryProperties(self,name):
        query = "SELECT partner_code_ FROM countries WHERE name = '{}'".format(name)
        df = self.get_table(query)
        pais = df['partner_code_'].values.tolist()[0]
        return pais
    def obtainProductoDescription(self,detalle=2):
        if detalle == 2:
            query = "SELECT * FROM descripcion_sa2"
        elif detalle == 4:
            query = "SELECT * FROM descripcion_sa2"
        elif detalle == 1:
            query = "SELECT * FROM sections"
        product_list = self.get_table(query)
        product_list = product_list['description']
        return product_list

    def grafica_treemap_paises(self,df,periodo=None,imp_exp=None):
        imp_exp = 'Importaciones' if imp_exp == 1 else 'Exportaciones'
        fig = px.treemap(df, 
                        path=['description','iso_3'], 
                        values='tradevalue',
                        title='{imp_exp} en millones de dólares ({año})'.format(imp_exp=imp_exp,año=periodo[0])
                        #color='porcentaje',
                        )
        fig.show()
    def grafica_treemap_paises_productos(self,df,periodo=None,imp_exp=None):
        imp_exp = 'Importaciones' if imp_exp == 1 else 'Exportaciones'
        fig = px.treemap(df, 
                        path=['description','SA_4'], 
                        values='tradevalue',
                        branchvalues='total',
                        #color='tradevalue',
                        title = '{imp_exp} en millones de dólares ({año})'.format(imp_exp=imp_exp,año=periodo[0]),
                        )
        fig.show()
    def grafica_destino_origen(self,df,periodo=None,imp_exp=None):
        imp_exp = 'Orígenes' if imp_exp == 1 else 'Destinos'
        df = df.groupby(['region','name','iso_3'],as_index=False)['tradevalue'].sum()
        total = df['tradevalue'].sum()
        df['porcentaje'] = df.groupby(['name'],group_keys=False)['tradevalue'].apply(lambda x: (x/total)*100)
        # #eliminar registros con porcentaje < 3
        # df = df[df['porcentaje'] > 3]
        # #df.tradevalue.quantile(0.25), df.tradevalue.quantile(0.7)
        # fig = px.choropleth(df, locations='iso_3', color='porcentaje',
        #                         color_continuous_scale="Viridis",
        #                         range_color=(df.tradevalue.quantile(0.25), df.tradevalue.quantile(0.9)), # range of values
        #                         labels={'aumento_disminucion':'porcentaje'},
        #                         title='{imp_exp} ({año})'.format(imp_exp=imp_exp,año=periodo[0])
        #                   )
        # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})                                
        # fig.show()
        fig = px.treemap(df, 
                        path=['region','iso_3'], 
                        values='tradevalue',
                        branchvalues='total',
                        #color='tradevalue',
                        title = '{imp_exp} ({año})'.format(imp_exp=imp_exp,año=periodo[0]),
                        )    
        fig.show()
    def cambio_porcentualImpExp(self):
        df = self.read_data()
        df =df.groupby(['year','imp_exp','partner_code','iso_3'],group_keys=False)[['tradevalue']].sum().reset_index()
        #paises unicos
        paises = df['partner_code'].unique()
        aumento_disminucion_pais = {}
        for pais in paises:
            df_pais = df[df['partner_code']==pais]
            df_pais=df_pais['tradevalue'].values.tolist()
            if len(df_pais) > 1:
                diff = ((df_pais[1]-df_pais[0])/df_pais[1]*100)
                aumento_disminucion_pais[pais] = diff
                #dicc to dataframe
        df_ = pd.DataFrame.from_dict(aumento_disminucion_pais,orient='index',columns=['aumento_disminucion'])
        df_['partner_code'] = df_.index
        df = df.merge(df_,how='inner',on='partner_code')
        return df
    
    def grafica_incrementoMercado_pais(self,df,scope_=None,periodo=None,imp_exp=None):
        periodo.sort()
        imp_exp = 'Importaciones' if imp_exp == 1 else 'Exportaciones'
        fig = px.choropleth(df, locations='iso_3', color='aumento_disminucion',
                                color_continuous_scale="Viridis",
                                range_color=(df.aumento_disminucion.quantile(0.25), df.aumento_disminucion.quantile(1)), # range of values
                                scope = scope_,
                                labels={'aumento_disminucion':'Aumento/disminucion'},
                                title='Cambio en el valor de importaciones del {} al {}'.format(periodo[0],periodo[1])
                          )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})                                
        fig.show()
    def ITrade_pricnipalesSocios(self):
        df = self.read_data()[0]

        df_usa = df[df['iso_3']=='USA']
        df_canada = df[df['iso_3']=='CAN']
        df_jpn= df[df['iso_3']=='JPN']
        df_ue = df[df['iso_3'].isin(['AUT','BEL','BGR','HRV','CYP','CZE','DNK','EST','FIN','FRA','DEU','GRC','HUN','IRL','ITA','LVA','LTU','LUX','MLT','NLD','POL','PRT','ROU','SVK','SVN','ESP','SWE','GBR'])]
        df_aliazna_pacifico = df[df['iso_3'].isin(['CHL','PER','COL'])]
        df_centroamerica = df[df['iso_3'].isin(['CUB','PAN','GTM','CRI','SLV','NIC','HND','DOM'])]

        #UNIR DATAFRAMES
        df = pd.concat([df_usa,df_canada,df_jpn,df_ue,df_aliazna_pacifico,df_centroamerica])
        #CREAR COLUMNA REGION
        df['region_'] = np.where(df['iso_3'].isin(['USA']),'USA',
                        np.where(df['iso_3'].isin(['CAN']),'CAN',
                        np.where(df['iso_3'].isin(['JPN']),'JPN',
                        np.where(df['iso_3'].isin(['AUT','BEL','BGR','HRV','CYP','CZE','DNK','EST','FIN','FRA','DEU','GRC','HUN','IRL','ITA','LVA','LTU','LUX','MLT','NLD','POL','PRT','ROU','SVK','SVN','ESP','SWE','GBR']),'UE',
                        np.where(df['iso_3'].isin(['CHL','PER','COL']),'ALIANZA PACIFICO',
                        np.where(df['iso_3'].isin(['CUB','PAN','GTM','CRI','SLV','NIC','HND','DOM']),'CENTROAMERICA',''))))))

        #IMPORTACIONES
        df_imp = df[(df['imp_exp']==1)]
        df.groupby(['year','imp_exp','region_'],group_keys=False)[['tradevalue']].sum().reset_index()
        df_imp = df_imp.groupby(['year','imp_exp','region_'],group_keys=False)[['tradevalue']].sum().reset_index()
        df_imp = df_imp.pivot(index='year',columns='region_',values='tradevalue')

        #EXPORTACIONES
        df_exp = df[(df['imp_exp']==2)]
        df_exp.groupby(['year','imp_exp','region_'],group_keys=False)[['tradevalue']].sum().reset_index()
        df_exp = df_exp.groupby(['year','imp_exp','region_'],group_keys=False)[['tradevalue']].sum().reset_index()
        df_exp = df_exp.pivot(index='year',columns='region_',values='tradevalue')
        fig = make_subplots(rows=2, cols=3,subplot_titles=('USA','CAN','UE','JPN','ALIANZA PACIFICO','CENTROAMERICA'))
        fig.add_trace(go.Scatter(x=df_imp.index, y=df_imp['USA'],line_color='green',name='Importaciones'),row=1, col=1),
        fig.add_trace(go.Scatter(x=df_exp.index, y=df_exp['USA'],line_color='blue',name='Exportaciones'),row=1, col=1),
        fig.add_trace(go.Scatter(x=df_imp.index, y=df_imp['CAN'],line_color='green',name='Importaciones',showlegend=False),row=1, col=2),
        fig.add_trace(go.Scatter(x=df_exp.index, y=df_exp['CAN'],line_color='blue',name='Exportaciones',showlegend=False),row=1, col=2),
        fig.add_trace(go.Scatter(x=df_imp.index, y=df_imp['UE'],line_color='green',name='Importaciones',showlegend=False),row=1, col=3),
        fig.add_trace(go.Scatter(x=df_exp.index, y=df_exp['UE'],line_color='blue',name='Exportaciones',showlegend=False),row=1, col=3),
        fig.add_trace(go.Scatter(x=df_imp.index, y=df_imp['JPN'],line_color='green',name='Importaciones',showlegend=False),row=2, col=1),
        fig.add_trace(go.Scatter(x=df_exp.index, y=df_exp['JPN'],line_color='blue',name='Exportaciones',showlegend=False),row=2, col=1),
        fig.add_trace(go.Scatter(x=df_imp.index, y=df_imp['ALIANZA PACIFICO'],line_color='green',name='Importaciones',showlegend=False),row=2, col=2),
        fig.add_trace(go.Scatter(x=df_exp.index, y=df_exp['ALIANZA PACIFICO'],line_color='blue',name='Exportaciones',showlegend=False),row=2, col=2),
        fig.add_trace(go.Scatter(x=df_imp.index, y=df_imp['CENTROAMERICA'],line_color='green',name='Importaciones',showlegend=False),row=2, col=3),
        fig.add_trace(go.Scatter(x=df_exp.index, y=df_exp['CENTROAMERICA'],line_color='blue',name='Exportaciones',showlegend=False),row=2, col=3),
        fig.update_layout(height=600, width=800, title_text="Intercambio comercial con socios princiapales (2015-2021)")
        fig.show()