'''Este script se encarga de extraer los datos de la página de la UN Comtrade de acuerdo al SA_4'''

#######################################################
import urllib.request, json
import requests
import pandas as pd
import numpy as np
import re
from mysql_db import MysqlDB
import os
import winsound



class Datos_comercio():
    def __init__(self,period,years,country_code,partner_code,archivo_,api,tabla,consulta_errores=False,extract2Vuelta=False):
        self.period = period
        self.years = years
        self.country_code = country_code
        self.partner_code = partner_code
        self.archivo_ = archivo_
        self.api = api
        self.tabla = tabla
        self.db = MysqlDB()
        self.consulta_errores = consulta_errores
        self.extract2Vuelta = extract2Vuelta
        if self.extract2Vuelta:
            self.new_petitions_urls()
        else:
            self.obtener_fracciones()

    def obtener_fracciones(self):
        archivo_categorias = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'files', self.archivo_))
        df = pd.read_csv(archivo_categorias, encoding='utf-8')
        codigos_productos = []
        descripcion_productos = []
        for i in range(1,97): 
            if i != 77:
                try:
                    l = df.iloc[:,i-1].dropna()
                    l=l.apply(lambda x: x[0:6].replace('.',"").strip())
                    desc = l.apply(lambda x: x[6:].replace('.',"").strip())
                    codigos_productos.append(l.values.tolist())
                except:
                    print('error en ', i)
        codigos_productos = [item for sublist in codigos_productos for item in sublist]
        '''2 PARA LA API NUEVA'''
        if self.api == 2:
            self.extract_data(years=self.years,country_code=self.country_code,product_codes=codigos_productos[342:])
        else:
            self.extract_data(period=self.period,years=self.years,country_code=self.country_code,partner_code=self.partner_code,product_codes=codigos_productos[0:1]) 
    
    def extract_data(self,years=None,country_code=None,product_codes=None,partner_code=None,period=None,url_=None):
        lista_errores = []
        for index,codigo in enumerate(product_codes):   
            print(f'Procesando {index} de {len(product_codes)}')
            try:
                if self.api == 2 and url_==None:
                    url = "https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode={}&period={}&cmdCode={}&flowCode=M,X&customsCode=C00&motCode=0".format(country_code,years,product_codes[index])
                elif self.api == 1 and url_==None:  
                    url = "http://comtrade.un.org/api/get?max=1000&type=C&freq={}&px=H0&ps={}&r={}&p={}&rg=all&cc={}".format(period,years,country_code,partner_code,product_codes[index])
                else:
                    url= url_.strip()
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
                    count = result['count']
                    if count >=500:
                        with open('files/urls.txt', 'a') as f:
                            f.write(url + ' \n')
                        continue
                    # elif count<450 and url_==None:
                    #     continue
                    df = pd.DataFrame(result['data'])
                    df = df.fillna(0)
                    df = df[['refYear','flowCode','partnerCode','primaryValue','fobvalue','qty','qtyUnitCode','netWgt','grossWgt']]
                    df = df.sort_values(by=['refYear','flowCode','primaryValue'],ascending=[True,True,False])
                    num_original = df.shape[0]
                    #eliminar duplicados
                    df = df.drop_duplicates(subset=['refYear','flowCode','partnerCode','primaryValue'],keep='first')
                    df = df.sort_values(by=['refYear','flowCode','primaryValue'],ascending=[True,True,False])
                    df['porcentaje'] = df.groupby(['refYear','flowCode'],group_keys=False)['primaryValue'].apply(lambda x: (x/(x.sum()/1.8))*100)
                    df = df[df['porcentaje'] > 1]
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
                    data['fobvalue'] = row.fobvalue
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
        
        
    def new_petitions_urls(self):  # genera url de peticiones más pequeñas para aquellas que llegaron al límeite de 500 registros 
        with open ('files/urls.txt', 'r') as f:
            urls = f.readlines()
        for url in urls:
            # hdr ={
            # # Request headers
            # 'Cache-Control': 'no-cache',
            # }
            # req = urllib.request.Request(url, headers=hdr)
            # req.get_method = lambda: 'GET'
            # response = urllib.request.urlopen(req)
            # print(response.getcode())
            # print(url)
            # result   = requests.get(url.strip()).json()
            # df = pd.DataFrame(result['data'])        
            # df = df.replace({np.NAN:0})
            # df = df[['refYear']].astype(int)
            # years = df['refYear'].unique()
            # try:
            #     max_year = years[-2]
            # except:
            #     max_year = years[-1]
            period_url_original_ = re.findall(r'&period=(.+)&cmdCode', url)[0]
            period_url_original = period_url_original_.split(',')
            #convertir los años a enteros
            period_url_original = [int(i) for i in period_url_original]

            # new_period1 = [year for year in period_url_original if year <= max_year]
            # new_period2 = [year for year in period_url_original if year > max_year]
            #concatenando los elementos de la lista new_period en una cadena de texto
            new_period1 = period_url_original[0]
            new_period2 = period_url_original[1]
            #new_period1 = ','.join(map(str, new_period1))
            #new_period2 = ','.join(map(str, new_period2))
            url_mod1 = url.replace(period_url_original_, str(new_period1))
            url_mod2 = url.replace(period_url_original_, str(new_period2))
            with open('files/urls2.txt', 'a') as f:
                f.write(url_mod1.strip() + ' \n')
                f.write(url_mod2.strip() + ' \n')
                
    def extractdata_segunda_vuelta(self):
        with open (r'C:\Users\ivan_\OneDrive - UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO\Desktop\repositorios\Comercio_exterior\files/urls2.txt','r') as f:
            urls = f.readlines()
        for url in urls:
            producto_code = re.findall(r'&cmdCode=(.+)&flowCode', url)
            self.extract_data(url_=url,product_codes=producto_code)




c = Datos_comercio('A','2013,2012','484','all','categorias.csv',2,'world_trade',extract2Vuelta=False)
if c.extract2Vuelta:
    #c.new_petitions_urls()
    c.extractdata_segunda_vuelta()
    

#d = Datos_comercio('A','2021,2020,2019,2018,2017,2016,2015,2014','484','all','categorias.csv',2,'world_trade_',True)
#d.errores()
#2009,2008,2007,2006,2005,2004,2003,2002,2001,2000s