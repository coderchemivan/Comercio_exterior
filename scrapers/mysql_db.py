import mysql.connector




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
            insertar_registro = "INSERT INTO world_trade_ (reporter_country,year,section,SA_4, imp_exp,partner_code,tradevalue,fobvalue,tradequantity,quantity_unit,netweight) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(insertar_registro, (diccionario['reporter_country'],
                                            diccionario['year'],
                                            diccionario['section'],
                                            diccionario['SA_4'],
                                            diccionario['imp_exp'],
                                            diccionario['partner_code'],
                                            diccionario['tradevalue'],
                                            diccionario['fobvalue'],
                                            diccionario['tradequantity'],
                                            diccionario['quantity_unit'],
                                            diccionario['netweight'],
                                            ))
        else:
            
            insertar_registro = "INSERT INTO world_trade (reporter_country,year,period,section,SA_4, imp_exp,partner_code,tradevalue,tradequantity,altquantity,netweight,grossweight) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(insertar_registro, (diccionario['reporter_country'],
                                            diccionario['year'],
                                            diccionario['period'],
                                            diccionario['section'],
                                            diccionario['SA_4'],
                                            diccionario['imp_exp'],
                                            diccionario['partner_code'],
                                            diccionario['tradevalue'],
                                            diccionario['tradequantity'],
                                            diccionario['altquantity'],
                                            diccionario['netweight'],
                                            diccionario['grossweight']))
        self.conn.commit()
        cur.close()
        self.conn.close

    def crear_tabla_secciones(self):
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE if not EXISTS sections (id INT AUTO_INCREMENT PRIMARY KEY, chapters VARCHAR(20))")
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
        cur.execute("SELECT chapters FROM sections")
        rows = cur.fetchall()
        rows,= list(zip(*rows))
        self.conn.commit()
        cur.close()
        return rows
    
    def verificar_partner_code_in_countriesTable(self):
        cur = self.conn.cursor()
        cur.execute("SELECT distinct(partner_code_)from world_trade_;")
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
    

#probando
# c = MysqlDB()
# m = c.verificar_partner_code_in_countriesTable()
# print(m)

#c.insertar_registro({'bilateral_dos_num': 1, 'bilateral_cuatro_num': 1020, 'imp_exp': 2, 'country': 'United States of America', 'año_2017': '682613', 'año_2018': '756178', 'año_2019': '824127', 'año_2020': '883174', 'año_2021': '485121'})