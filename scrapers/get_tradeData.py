'''Este script se encarga de extraer los datos de la página de la UN Comtrade de acuerdo al SA_4'''

#######################################################
import urllib.request, json
import requests
import pandas as pd
import numpy as np
from mysql_db import MysqlDB
import os
import winsound



class Datos_comercio():
    def __init__(self,period,years,country_code,partner_code,archivo_,api,tabla,consulta_errores=False):
        self.period = period
        self.years = years
        self.country_code = country_code
        self.partner_code = partner_code
        self.archivo_ = archivo_
        self.api = api
        self.tabla = tabla
        self.db = MysqlDB()
        self.consulta_errores = consulta_errores
        if self.consulta_errores:
            self.errores()
        else:
            self.obtener_fracciones()

    def obtener_fracciones(self):
        archivo_categorias = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'files', self.archivo_))
        df = pd.read_csv(archivo_categorias, encoding='utf-8')
        codigos_productos = []
        for i in range(1,97): 
            if i != 77:
                try:
                    l = df.iloc[:,i-1].dropna()
                    l=l.apply(lambda x: x[0:6].replace('.',"").strip())
                    codigos_productos.append(l.values.tolist())
                except:
                    print('error en ', i)
        codigos_productos = [item for sublist in codigos_productos for item in sublist]
        '''2 PARA LA API NUEVA'''
        if self.api == 2:
            self.extract_data(years=self.years,country_code=self.country_code,product_codes=codigos_productos[540:])
        else:
            self.extract_data(period=self.period,years=self.years,country_code=self.country_code,partner_code=self.partner_code,product_codes=codigos_productos[0:]) 
    
    def extract_data(self,years,country_code,product_codes,partner_code=None,period=None):
        lista_errores = []
        for index,codigo in enumerate(product_codes):   
            print(f'Procesando {index} de {len(product_codes)}')
            try:
                if self.api == 2:
                    url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode={}&period={}&cmdCode={}&flowCode=M,X&customsCode=C00&motCode=0".format(country_code,years,product_codes[index])
                else:    
                    url = "http://comtrade.un.org/api/get?max=1000&type=C&freq={}&px=H0&ps={}&r={}&p={}&rg=all&cc={}".format(period,years,country_code,partner_code,product_codes[index])
                print(url)
                hdr ={
                # Request headers
                'Cache-Control': 'no-cache',
                }
                req = urllib.request.Request(url, headers=hdr)
                req.get_method = lambda: 'GET'
                response = urllib.request.urlopen(req)
                print(response.getcode())
                result   = requests.get(url).json()
                

                if self.api ==2:
                    df = pd.DataFrame(result['data'])
                    df = df.fillna(0)
                    df = df[['refYear','flowCode','partnerCode','primaryValue','qty','qtyUnitCode','netWgt','grossWgt']]
                    df = df.sort_values(by=['refYear','flowCode','primaryValue'],ascending=[True,True,False])
                    num_original = df.shape[0]/2
                    #print(df.columns)
                        #eliminar a los países que participen con menos del 3% del total
                    df = df.groupby(['refYear','flowCode','partnerCode']).sum().reset_index()
                    df = df.sort_values(by=['refYear','flowCode','primaryValue'],ascending=[True,True,False])
                    df['porcentaje'] = df.groupby(['refYear','flowCode'])['primaryValue'].apply(lambda x: x/(x.sum()/2))    
                    df = df[df['porcentaje'] > 0.01]
                else:
                    df = pd.DataFrame(result['dataset'])
                    df = df.replace({np.NAN:0})
                    df = df[['yr','period','rgCode','ptCode','TradeValue','TradeQuantity','quantity_unit','NetWeight','GrossWeight']]
                    df = df.sort_values(by=['yr','rgCode','period','ptCode'],ascending=[True,True,True,True])
                    df = df.groupby(['yr','rgCode','ptCode']).sum().reset_index()
                    df = df.sort_values(by=['yr','rgCode','TradeValue'],ascending=[True,True,False])
                    df['porcentaje'] = df.groupby(['yr','rgCode'])['TradeValue'].apply(lambda x: x/(x.sum()/2))    
                    df = df[df['porcentaje'] > 0.03]              


                print(df)
                print(num_original,df.shape[0])
                
                self.insert_data(df,product_codes[index])
                
            except Exception as e:
                print(e)
                lista_errores.append([url,e])

        if len(lista_errores) > 0:
            print('Errores en las siguientes urls: ', lista_errores,len(lista_errores))
        self.avisar_termino()

    def insert_data(self,df,product_code):
        data = {}
        data_ =[]
        for row in df.itertuples():
            try:
                if self.api ==2:
                    data['year'] = row.refYear
                    data['imp_exp'] = row.flowCode.replace('X',str(2)).replace('M',str(1))
                    data['partner_code'] = row.partnerCode
                    data['tradevalue'] = row.primaryValue
                    data['tradequantity'] = row.qty
                    data['quantity_unit'] = row.qtyUnitCode
                    data['netweight'] = row.netWgt
                    data['grossweight'] = row.grossWgt
                else:
                    data['year'] = row.yr
                    data['period'] = row.period
                    data['imp_exp'] = row.rgCode
                    data['partner_code'] = row.ptCode
                    data['tradevalue'] = row.TradeValue
                    data['tradequantity'] = row.TradeQuantity
                    data['altquantity'] = row.AltQuantity
                    data['netweight'] = row.NetWeight
                    data['grossweight'] = row.GrossWeight
            except  Exception as e:
                print(e)
                continue

            section = self.consult_section(product_code[0:2])
            data['reporter_country'] = self.country_code
            data['section'] = section
            data['SA_2'] = product_code[0:2]
            data['SA_4'] = product_code
            data_.append(data)
            try:
                self.db.insertar_registro(self.tabla,data)
            except Exception as e:
                print(e)
                continue
    def consult_section(self,sa_2):
        if sa_2.startswith('0'):
            sa_2 = sa_2[1:]
        sections = self.db.consultar_sections()
        for index,section in enumerate(sections):
            rango = section.split('-')
            if rango[0] == sa_2:
                if int(sa_2) == int(rango[0]):
                    break
            if len(rango)>1 and int(sa_2) >= int(rango[0]) and int(sa_2) <= int(rango[1]):
                break
        return index+1

    def avisar_termino(self):
        duration = 1000  # milliseconds
        freq = 440  # Hz
        winsound.Beep(freq, duration)

    def errores(self):
        #years,country_code,product_codes,partner_code=None,period=None
        years = '2010,2011,2012,2013,2014,2015,2016,2017,2018'
        country_code = '484'
        errores =  ['https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=2934&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=2935&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=4907&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=5001&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=5003&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=5005&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=5102&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=5104&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=5108&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=5110&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=5113&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7111&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7412&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7413&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7415&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7418&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7419&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7501&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7502&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7503&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7504&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7505&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7506&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7507&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7508&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7601&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7602&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7603&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7604&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7605&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7606&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7607&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7608&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7609&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7610&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7611&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7612&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7613&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7614&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7615&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7616&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7901&flowCode=M,X&customsCode=C00&motCode=0', 
        'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7902&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7903&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7904&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7905&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=7907&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8001&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8002&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8003&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8007&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8101&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8102&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8103&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8104&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8105&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8106&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8107&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8108&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8109&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8110&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8111&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8112&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8113&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8201&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8202&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8203&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8204&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8205&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8206&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8207&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8208&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8209&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8210&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8211&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8212&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8213&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8214&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8215&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8301&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8302&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8303&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8304&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8305&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8306&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8307&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8308&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8309&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8310&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8311&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8401&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8402&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8403&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8404&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8405&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8406&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8407&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8408&flowCode=M,X&customsCode=C00&motCode=0', 'https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=484&period=2021,2020,2019,2018,2017,2016,2015,2014&cmdCode=8908&flowCode=M,X&customsCode=C00&motCode=0']
        for error in errores:
            print(error[0])
        
    

c = Datos_comercio('A','2008,2007,2006,2005,2004,2003,2002,2001,2000','484','all','categorias.csv',2,'world_trade_')
#d = Datos_comercio('A','2021,2020,2019,2018,2017,2016,2015,2014','484','all','categorias.csv',2,'world_trade_',True)
#d.errores()