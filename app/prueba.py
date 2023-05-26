
from data_processing.data_processing import Data


df = df_inicial_ = Data('world_trade_',fuente_datos='csv',year=[2015,2016,2017,2018,2019,2020,2021]).read_data()
print(df)