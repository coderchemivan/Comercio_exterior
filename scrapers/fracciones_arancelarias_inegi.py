from bs4 import BeautifulSoup
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup
import re
from time import sleep

import pandas as pd
from itertools import zip_longest


class fracciones_arancelarias_inegi():
    def __init__(self):
        self.url = "https://www.inegi.org.mx/app/tigie/"
        self.driver = self.get_driver()
        self.get_data()
        self.driver.quit()


    def get_driver(self):
        opts = Options()
        opts.add_argument(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36.")
        driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()),options=opts)
        driver.get(self.url)
        sleep(5)
        categorias_ ={}
        categorias = driver.find_elements(By.XPATH,"//*[@class='curs-txt']")
        categorias = [x.text for x in categorias]

        for i in range(1,96):
            if i != 77:
                try:
                    buton_mas = driver.find_element(By.XPATH,"//span[@id='boton_{i}']".format(i=str(i).zfill(2)))
                    buton_mas.click()
                    sleep(1)
                    subcategorias = [x.text.strip() for x in driver.find_elements(By.XPATH,'//*[@id="ul_{i_}"]/li/span'.format(i_=str(i).zfill(2), i = str(i)))]
                    subcategorias = [x for x in subcategorias if x != '']
                    categorias_[categorias[i-1]] = subcategorias

                except:
                    print('error en ', i)
        self.guarar(categorias_)
                    
        def guardar_datos(diccionario,archivo):
            df =  pd.DataFrame(zip_longest(*diccionario.values()), columns=diccionario)
            df.to_csv('categorias.csv', index=False)   


c = fracciones_arancelarias_inegi()










