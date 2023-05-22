import mysql.connector
import pandas as pd
import json

class MysqlDB():
    def __init__(self):
       self.conn = mysql.connector.connect(user="root", password="123456",
                                       host="localhost",
                                       database="mexico_it",
                                       port='3306'
                                       )
    def insertar_registro(self,tabla,diccionario):
        cur = self.conn.cursor()
        if tabla =='world_trade_':
            insertar_registro = "INSERT INTO world_trade_ (reporter_country,year,section,SA_4, imp_exp,partner_code,tradevalue,tradequantity,netweight) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(insertar_registro, (diccionario['reporter_country'],
                                            diccionario['year'],
                                            diccionario['section'],
                                            diccionario['SA_4'],
                                            diccionario['imp_exp'],
                                            diccionario['partner_code'],
                                            diccionario['tradevalue'],
                                            diccionario['tradequantity'],
                                            diccionario['netweight'],
                                            ))
        else:
            
            insertar_registro =  "INSERT INTO world_trade (reporter_country,year,section,SA_4, imp_exp,partner_code,tradevalue,tradequantity,netweight) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            
            cur.execute(insertar_registro, (diccionario['reporter_country'],
                                            diccionario['year'],
                                            diccionario['section'],
                                            diccionario['SA_4'],
                                            diccionario['imp_exp'],
                                            diccionario['partner_code'],
                                            diccionario['tradevalue'],
                                            diccionario['tradequantity'],
                                            diccionario['netweight'],
                                            ))
        self.conn.commit()
        cur.close()
        self.conn.close

    def crear_tabla_secciones(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE if not EXISTS sections_ (id INT AUTO_INCREMENT PRIMARY KEY, chapters VARCHAR(20))")
        cur.execute('''
                        INSERT INTO sections (chapters) VALUES
                        ('1-5'),
                        ('6-14'),
                        ('15'),
                        ('16-24'),
                        ('25-27'),
                        ('28-38'),
                        ('39-40'),
                        ('41-43'),
                        ('44-46'),
                        ('47-49'),
                        ('50-63'),
                        ('64-67'),
                        ('68-70'),
                        ('71'),
                        ('72-83'),
                        ('84-85'),
                        ('86-89'),
                        ('90-92'),
                        ('93'),
                        ('94-96'),
                        ('97')
                        ''')
        self.conn.commit()
        cur.close()
        self.conn.close()

    def consultar_sections(self):
        cur = self.conn.cursor()
        cur.execute("SELECT chapters FROM sections_")
        rows = cur.fetchall()
        rows,= list(zip(*rows))
        self.conn.commit()
        cur.close()
        return rows
    
    def verificar_partner_code_in_countriesTable(self):
        cur = self.conn.cursor()
        cur.execute("SELECT distinct(partner_code)from world_trade_;")
        rows = cur.fetchall()
        rows,= list(zip(*rows))
        self.conn.commit()
        
        for row in rows:
            cur.execute("SELECT name FROM countries WHERE partner_code_ = %s", (row,))
            name = cur.fetchone()
            if name is None:
                print(row)
                #cur.execute("INSERT INTO countries (partner_code_) VALUES (%s)", (row,))
        cur.close()  
        return rows
    
    def eliminar_registros_insignificantes(self):
        #Eliminar registros con valores con porcentaje menor a 3
        cur = self.conn.cursor()
        cur.execute("SELECT FROM world_trade_")
        rows = cur.fetchall()
        world_tradeTable = pd.DataFrame(rows,columns=[x[0] for x in cur.description])['year']
        print(world_tradeTable.shape[0])
        world_tradeTable['section'] = world_tradeTable['section'].astype(int)
        world_tradeTable = world_tradeTable[~(world_tradeTable['partner_code']=='0')] 
        world_tradeTable['porcentaje'] = world_tradeTable.groupby(['year','imp_exp','SA_4'],group_keys=False)['tradevalue'].apply(lambda x: (x/(x.sum()))*100)
        world_tradeTable['porcentaje'] = world_tradeTable['porcentaje'].round(2)
        world_tradeTable = world_tradeTable[world_tradeTable['porcentaje'] > 3] 
        print(world_tradeTable.shape[0])
    
    def anadir_region_countries(self):
        cur = self.conn.cursor()
        cur.execute("SELECT iso_3 FROM countries")
        rows = cur.fetchall()
        #rows a lista
        rows,= list(zip(*rows))
        print(len(rows))

        for row in rows:
            try:
                cur.execute("SELECT region from countries_ WHERE iso_3 ='{}'".format(str(row)))
                region = cur.fetchone()[0]
                #update column region in countries table
                cur.execute("UPDATE countries SET region = %s WHERE iso_3 = %s", (region,row))
            except  Exception as e:
                print(e)
                continue
        self.conn.commit()
        cur.close()
        self.conn.close()

    def createTablaSA2Description(self):
        cur = self.conn.cursor()
        #open i2020.json
        with open(r'C:\Users\ivan_\OneDrive - UNIVERSIDAD NACIONAL AUTÓNOMA DE MÉXICO\Desktop\repositorios\Comercio_exterior\scrapers/i2016.json',encoding='utf-8') as json_file:
            data = json.load(json_file)
        
        #cur.execute("CREATE TABLE if not EXISTS sections_ (id , description VARCHAR(250))")
        for row in data:
            #ssa4 son los último 4 dígitos de 'HS4 ID'
            sect = str(row['Section ID'])
            #print(row['Section'])
            
            #print(sa4,row['HS4 ID'])
            try:
                cur.execute("INSERT INTO sections_ (id,description) VALUES (%s,%s)", (sect,row['Section']))
            except Exception as e:
                print(e)
                continue
                
        self.conn.commit()
        cur.close()
        self.conn.close()






#c = MysqlDB().createTablaSA2Description()
# print(c)