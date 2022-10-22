# from bs4 import BeautifulSoup
# import requests

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from time import sleep
# from bs4 import BeautifulSoup
# import re
# from time import sleep

# import pandas as pd
# from itertools import zip_longest


# opts = Options()
# opts.add_argument(
#              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36.")
# driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()),options=opts)


# driver.get('https://www.inegi.org.mx/app/tigie/')


# sleep(5)

# categorias_ ={}
# categorias = driver.find_elements(By.XPATH,"//*[@class='curs-txt']")
# categorias = [x.text for x in categorias]

# for i in range(1,96):
#     if i != 77:
#         try:
#             buton_mas = driver.find_element(By.XPATH,"//span[@id='boton_{i}']".format(i=str(i).zfill(2)))
#             buton_mas.click()
#             sleep(1)
#             subcategorias = [x.text.strip() for x in driver.find_elements(By.XPATH,'//*[@id="ul_{i_}"]/li/span'.format(i_=str(i).zfill(2), i = str(i)))]
#             subcategorias = [x for x in subcategorias if x != '']
#             categorias_[categorias[i-1]] = subcategorias

#         except:
#             print('error en ', i)
            
# driver.close()

# df =  pd.DataFrame(zip_longest(*categorias_.values()), columns=categorias_)
# df.to_csv('categorias.csv', index=False)

#psando el dict a csv


import requests
from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.crawler import CrawlerProcess
import pandas as pd
from bs4 import BeautifulSoup
from lxml import etree
import ssl
from urllib3.exceptions import InsecureRequestWarning
from mysql_db import MysqlDB


df = pd.read_csv('files/categorias.csv', encoding='utf-8')

categorias = []
for i in range(1,3):
    if i != 77:
        try:
            l = df.iloc[:,i-1].dropna()
            l=l.apply(lambda x: x[0:6].replace('.',"").strip())
            categorias.append(l.values.tolist())
        except:
            print('error en ', i)

print(categorias)

for i in range(len(categorias)):
    urls = categorias[i]
    for j in range(len(urls)):
        for imp_exp_ in range(1,3):   #1= importaciones, 2 =exportaciones
            url = 'https://www.trademap.org/Country_SelProductCountry_TS.aspx?nvpm=1%7c484%7c%7c%7c%7c{id}%7c%7c%7c4%7c1%7c1%7c{imp_exp}%7c2%7c1%7c2%7c1%7c1%7c1'.format(id = categorias[i][j].strip(),imp_exp=imp_exp_)
            
            HEADERS = ({'User-Agent':
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
                        'Accept-Language': 'en-US, en;q=0.5'})
            
            webpage = requests.get(url, headers=HEADERS,verify=False)
            soup = BeautifulSoup(webpage.content, "html.parser")
            dom = etree.HTML(str(soup))

            l = dom.xpath('//td[@class="tabContent"]')

            headers = dom.xpath("//td[@class='tabContent']//tr[1]//th//text()")
            if len(headers) > 0:
                c = 1
                r = 0 
            else:
                c = 2 
                r = 1
                headers = dom.xpath("//td[@class='tabContent']//tr[2]//th//text()")
            rows = dom.xpath("//td[@class='tabContent']//tr[position()>{c}]".format(c=c))
            rows = rows[:len(rows)-r]
            if len(rows)>0:
                print('__________________________')
                print(categorias[i][j])
                print(url)       
                data = {}
                data_ =[]
                for row in rows:
                    datos = row.xpath(".//td//text()")[2:]
                    datos = [x for x in datos if x != '\n']
                    datos = ['0'  if x == '\xa0' else x for x in datos]
                    data['SA_2'] = categorias[i][j][0:2]
                    data['SA_4'] = categorias[i][j]
                    data['imp_exp'] = imp_exp_
                    data['country'] = datos[0]
                    data['año_2017'] = datos[1].replace(',','')
                    data['año_2018'] = datos[2].replace(',','')
                    data['año_2019'] = datos[3].replace(',','')
                    data['año_2020'] = datos[4].replace(',','')
                    data['año_2021'] = datos[5].replace(',','')
                    c = MysqlDB()
                    c.insertar_registro(data)
                    data_.append(datos)
                df = pd.DataFrame(data_, columns=headers[1:])
                print(df)


