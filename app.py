#Autor: Lucas Tavares dos Santos

#from asyncio.windows_events import NULL
import select
import matplotlib
import json

from getData import getDataAno
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from prophet import Prophet
from flask import Flask, render_template, request
app = Flask(__name__)
from getData import getDataAtDB
import numpy as np
from datetime import date
from flask_cors import CORS

cors = CORS(app, resources={r"/*": {"origins": "https://usp-municipios.vercel.app/"}})

# from fbprophet.diagnostics import cross_validation, performance_metrics
# import itertools

# def create_param_combinations(**param_dict):
#     param_iter = itertools.product(*param_dict.values())
#     params =[]
#     for param in param_iter:
#         params.append(param) 
#     params_df = pd.DataFrame(params, columns=list(param_dict.keys()))
#     return params_df

# def single_cv_run(history_df, metrics, param_dict, parallel):
#     m = Prophet(**param_dict)
#     m.add_country_holidays(country_name='BR')
#     history_df['cap'] = 2*history_df["y"].max()
#     m.fit(history_df)
#     df_cv = cross_validation(m, initial='3600 days', horizon = '1200 days', parallel=parallel)
#     df_p = performance_metrics(df_cv, rolling_window=1)
#     df_p['params'] = str(param_dict)
#     print(df_p.head())
#     df_p = df_p.loc[:, metrics]
#     return df_p

# param_grid = {  
#                 'changepoint_prior_scale': [0.05, 0.5, 5],
#                 'changepoint_range': [0.8, 0.9],
#               }
# metrics = ['horizon', 'rmse', 'mdape', 'params'] 
# results = []



@app.route('/')

# @app.route('/teste', methods=['GET','POST'])
# def teste():
#     select_ano = request.form.get("Anos", None)
#     select_mun = request.form.get("Municipios", None)
#     select_dp = request.form.get("Delegacias", None)
#     select_crime = request.form.get("Crimes", None)

#     df = getDataAtDB(select_mun, select_dp, select_crime)
#     df['datas'] = pd.to_datetime(df['datas'])

#     df.set_index('datas')
#     df.columns = ["ds", "y"]
#     return "Hello World!"

@app.route('/index.html')
def index():
    return render_template("index.html")

@app.route('/equipe.html')
def equipe():
    return render_template("equipe.html")

@app.route('/previsao.html')
def projeto():
    return render_template("previsao.html")

@app.route('/PlotSeries', methods=['GET','POST'])
def PlotSeries():
    
    #obtém valores de selects da pagina
    select_ano = request.form.get("Anos", None)
    select_mun = request.form.get("Municipios", None)
    select_dp = request.form.get("Delegacias", None)
    select_crime = request.form.get("Crimes", None)

    if select_mun != None and select_mun != "" and select_dp != None and select_dp != "" and select_crime != None and select_crime != "":
        
        #dá um nome para o arquivo do plot
        img = 'static/plot' + select_ano + select_mun + select_dp + select_crime + '.png'

        #obtém o dataframe
        df = getDataAtDB(select_mun, select_dp, select_crime)
        df['datas'] = pd.to_datetime(df['datas'])

        #altera colunas do dataframe
        df.set_index('datas')
        df.columns = ["ds", "y"]

        #cria um modelo
        m = Prophet(
            changepoint_prior_scale=0.05,
            changepoint_range=0.8
        )
        m.add_country_holidays(country_name='BR')
        m.fit(df)

        #prevendo o futuro
        future = m.make_future_dataframe(periods=12*int(select_ano), freq='MS')
        forecast = m.predict(future)

        #cria imagem do plot
        m.plot(forecast, figsize=(8,4))
        plt.xlabel('Data')
        plt.ylabel('Ocorrencias')
        plt.gca().set_ylim(bottom=0)
        plt.title("Série temporal das ocorrências de " + select_crime + " registradas no " + select_dp)
        plt.savefig(img, bbox_inches='tight')

        plt.clf() #limpa figura atual
        
        # df_cv = cross_validation(m, initial='3600 days', horizon = '1200 days', parallel="processes")
        # df_p = performance_metrics(df_cv)
        # print(df_p.head())
        
        #Otimização dos hiperparametros
        # params_df = create_param_combinations(**param_grid)
        # print(len(params_df.values))
        # for param in params_df.values:
        #     param_dict = dict(zip(params_df.keys(), param))
        #     cv_df = single_cv_run(df, metrics, param_dict, parallel="processes")
        #     results.append(cv_df)
        # results_df = pd.concat(results).reset_index(drop=True)
        # best_param = results_df.loc[results_df['rmse'] == min(results_df['rmse']), ['params']]
        # print(f'\n The best param combination is {best_param.values[0][0]}')
        # print(results_df)

        return render_template("previsao.html", image = img)

    return render_template("previsao.html")

@app.route('/ReturnData', methods=['GET','POST'])
def ReturnData():

    ano_ini = request.form.get("inicio")
    ano_fim = request.form.get("fim")

    if(int(ano_fim) <= 2021):
        select_ano = 0 
    else :select_ano = int(ano_fim) - 2021 
    
    select_mun = request.form.get("Municipios", None)
    select_dp = request.form.get("Delegacias", None)
    select_crime = request.form.get("Crimes", None)

    df = getDataAtDB(select_mun, select_dp, select_crime)
    df['datas'] = pd.to_datetime(df['datas'])
    #df['ano'] = df['datas'].dt.year
    df.set_index('datas')
    df.columns = ["ds", "y"]
    m = Prophet(
            changepoint_prior_scale=0.05,
            changepoint_range=0.8
        )
    m.add_country_holidays(country_name='BR')
    m.fit(df)
    
    future = m.make_future_dataframe(periods=12*int(select_ano), freq='MS')
    forecast = m.predict(future)
    forecast['trend'] = forecast['trend'].apply(np.floor)
    forecast.resample('AS', on='ds').sum()

    years = int(ano_fim)+1 - int(ano_ini)

    output = np.zeros(years)
    output = output.tolist()

    teste = forecast['trend']

    teste = teste.to_numpy()
    teste = np.flip(teste)
    teste = teste.tolist()
    initial_len = len(teste) -1
    if len(teste) < len(output) : 
        for idx, val in enumerate(output):
            if idx <= initial_len:
                None
            else: 
                teste.append('0')
        output = teste
    else:
        for idx, val in enumerate(output):
            output[idx] = teste[idx]

    output.reverse()
    data = {"data": output}

    return data

# @app.route('/Teste', methods=['GET','POST'])
# def Teste():
#     today = date.today()
#     select_mun = request.form.get("Municipios", None)
#     select_dp = request.form.get("Delegacias", None)
#     ano_fim = int(request.form.get("Ano", None))
#     ano_ini = ano_fim
#     forecast_yrs = ano_fim - today.year + 1
    
#     crimes = [
#     "Homicídio Doloso", 
#     "Homicídio Doloso por acidente de trânsito", 
#     "Homicídio Culposo por acidente de trânsito", 
#     "Homicídio Culposo - Outros", 
#     "Tentativa de Homicídio", 
#     "Lesão Corporal seguida de morte",
#     "Lesão Corporal Dolosa",
#     "Lesão Corporal Culposa por acidente de trânsito",
#     "Lesão Corporal Culposa - Outras",
#     "Latrocínio",
#     "Estupro",
#     "Roubo - Outros",
#     "Roubo de veículo",
#     "Roubo a banco",
#     "Roubo de carga",
#     "Furto - Outros",
#     "Furto de veículo"
#     ], 
           
#     result = np.zeros(17)
#     result = result.tolist()
#     df = pd.DataFrame()
#     list = []
#     for i, aux in enumerate(crimes[0]):
#         df = getDataAtDB(select_mun, select_dp, crimes[0][i])
#         df['datas'] = pd.to_datetime(df['datas'])
#         df.set_index('datas')
#         df.columns = ["ds", "y"]
#         m = Prophet(
#         changepoint_prior_scale=0.05,
#         changepoint_range=0.8
#             )
#         m.add_country_holidays(country_name='BR')
#         m.fit(df)
#         future = m.make_future_dataframe(periods=12*forecast_yrs, freq='MS')
#         forecast = m.predict(future)
#         print(forecast)
        # forecast['trend'] = forecast['trend'].apply(np.floor)
        # forecast.resample('AS', on='ds').sum()

        # years = int(ano_fim)+1 - int(ano_ini)

        # output = np.zeros(years)
        # output = output.tolist()

        # teste = forecast['trend']

        # teste = teste.to_numpy()
        # teste = np.flip(teste)
        # teste = teste.tolist()
        # initial_len = len(teste) -1
        # if len(teste) < len(output) : 
        #     for idx, val in enumerate(output):
        #         if idx <= initial_len:
        #             None
        #         else: 
        #             teste.append('0')
        #     output = teste
        # else:
        #     for idx, val in enumerate(output):
        #         output[idx] = teste[idx]

        # output.reverse()
        # print(output)
    #     list.append(output)
    # return {"data": list}    
        #print(forecast)
    #return {}
        
    #     df['datas'] = pd.to_datetime(df['datas'])
    #     #df['ano'] = df['datas'].dt.year
    #     df.set_index('datas')
    #     df.columns = ["ds", "y"]
    #     return df.to_json(orient='records')
    #     m = Prophet(
    #             changepoint_prior_scale=0.05,
    #             changepoint_range=0.8
    #         )
    #     m.add_country_holidays(country_name='BR')
    #     m.fit(df)
        
    #     future = m.make_future_dataframe(periods=12*int(select_ano), freq='MS')
    #     forecast = m.predict(future)
    #     forecast['trend'] = forecast['trend'].apply(np.floor)
    #     forecast.resample('AS', on='ds').sum()

    #     years = int(ano_fim)+1 - int(ano_ini)

    #     output = np.zeros(years)
    #     output = output.tolist()

    #     teste = forecast['trend']

    #     teste = teste.to_numpy()
    #     teste = np.flip(teste)
    #     teste = teste.tolist()
    #     initial_len = len(teste) -1
    #     if len(teste) < len(output) : 
    #         for idx, val in enumerate(output):
    #             if idx <= initial_len:
    #                 None
    #             else: 
    #                 teste.append('0')
    #         output = teste
    #     else:
    #         for idx, val in enumerate(output):
    #             output[idx] = teste[idx]

    #     output.reverse()
    #     print(output)
    #     result.append(output[0])

    # return {"data": result}
        

    # if(int(select_ano) > 2021):

    #     forecast_yrs = select_ano - today.year + 1
    #     df = getDataAno(select_dp, select_ano)
    #     df['datas'] = pd.to_datetime(df['datas'])
    #     df.columns = ["type","ds", "y"]
    #     df_by_type = df.groupby('type')
    #     return df.to_json(orient='records')
    #     # for index, row in df.iterrows():
    #     #     print(row['c1'], row['c2'])
    #     #     df.set_index('datas')
    #     #     df.columns = ["type","ds", "y"]
    #     #     m = Prophet(
    #     #         changepoint_prior_scale=0.05,
    #     #         changepoint_range=0.8
    #     #     )
    #     #     m.add_country_holidays(country_name='BR')
    #     #     m.fit(df)
    #     #     future = m.make_future_dataframe(periods=12*int(forecast_yrs), freq='MS')
    #     #     forecast = m.predict(future)
        
    #     # return forecast.to_json(orient='records')
    # else:
    #     df = getDataAno(select_dp, select_ano)
    #     return df.to_json(orient='records')

if __name__ == "__main__":
    app.run()