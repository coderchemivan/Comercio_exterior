import mysql.connector




class MysqlDB():
    def __init__(self):
       self.conn = mysql.connector.connect(user="root", password="123456",
                                       host="localhost",
                                       database="mexico_it",
                                       port='3306'
                                       )
    def insertar_registro(self,diccionario):
        cur = self.conn.cursor()
        insertar_registro = "INSERT INTO trade (SA_2,SA_4, imp_exp,country,año_2017,año_2018,año_2019,año_2020,año_2021) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur.execute(insertar_registro, (diccionario['SA_2'],diccionario['SA_4'], diccionario['imp_exp'], diccionario['country'], diccionario['año_2017'], diccionario['año_2018'], diccionario['año_2019'], diccionario['año_2020'], diccionario['año_2021']))
        self.conn.commit()
        cur.close()
        self.conn.close





#probando

#c = MysqlDB()
#c.insertar_registro({'bilateral_dos_num': 1, 'bilateral_cuatro_num': 1020, 'imp_exp': 2, 'country': 'United States of America', 'año_2017': '682613', 'año_2018': '756178', 'año_2019': '824127', 'año_2020': '883174', 'año_2021': '485121'})