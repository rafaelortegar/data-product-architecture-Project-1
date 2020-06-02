import luigi
import logging
import psycopg2
import sqlalchemy
import pickle
import boto3

import pandas.io.sql as psql
import pandas as pd

from sqlalchemy import create_engine
from luigi.contrib.s3 import S3Target

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

from featureEngineering2 import featureEngineering2
from metadataFeatureEngineering import metadataFeatureEngineering
from metadataTestFeatureEng import metadataTestFeatureEng
from modelingMetro2 import modelingMetro2

import modelado
import prediction
from feature_builder import FeatureBuilder



class predictionMetro(luigi.Task):
    """
    Falta el comentario
    """

    #==============================================================================================================
    # Parameters
    #==============================================================================================================
    task_name = 'predictionMetro_task_07_01'
    date = luigi.Parameter()
    bucket = luigi.Parameter(default='dpaprojs3') # default='dpaprojs3')
    #==============================================================================================================
    
    # Indica que para iniciar loadCleaned proceso de carga de metadatos requiere que el task de extractToJson esté terminado
    def requires(self):
        return modelingMetro2(bucket=self.bucket, date=self.date) # , metadataCleaned(bucket = self.bucket, date=  self.date)

    def _requires(self):
        return {'a': metadataTestFeatureEng(bucket=self.bucket,date=self.date), 'b': [metadataFeatureEngineering(bucket=self.bucket,date=self.date)]}

    def run(self):
        creds = pd.read_csv("../../../credentials_postgres.csv")
        creds_aws = pd.read_csv("../../../credentials.csv")
        
        # Conectamos al bucket
        ses = boto3.session.Session(profile_name='rafael-dpa-proj') # , region_name='us-west-2') # Pasamos los parámetros apra la creación del recurso S3 (bucket) al que se va a conectar
        s3_resource = ses.resource('s3')
        obj = s3_resource.Bucket(self.bucket) # metemos el bucket S3 en una variable obj
        
        # conectamos a la RDS
#        connection = psycopg2.connect(user=creds.user[0],
#                                  password=creds.password[0],
#                                  host=creds.host[0],
#                                  port=creds.port[0],
#                                  database=creds.db[0])
#        
#        cursor = connection.cursor()
        
        # Leemos los datos de la RDS
        #df = psql.read_sql('SELECT * FROM semantic.metro;', connection)
        #print(df.shape) 
        
        # Cargamos el modelo
        file = open('modelo.pkl', 'rb')
        data = pickle.load(file)
        file.close()
        modelos = data.copy()
        
        df = pd.read_csv('x_original.csv')
        print("shape de lo leido",df.shape)
#        fecha = '2020-06-02'
        
        fecha = self.date
        
        pred = prediction.Predict()
        print(pred)
        pred = pred.predict(fecha, df, modelos)
        print(pred)
        print(pred.shape)
        
        # para los outputs que no vamos a usar
        
        fecha = pred['fecha'][0]
        linea = pred['linea'][0]
        estacion = pred['estacion'][0]
        pronostico_afluencia = pred['pronostico_afluencia'][0]
        datos_a_csv = {'fecha':[fecha],'linea':[linea],'estacion':[estacion],'pronostico_afluencia':[pronostico_afluencia]} 
        pandas_a_csv = pd.DataFrame(data=datos_a_csv)
        print("dimensiones de prediccion pandas_a_csv",pandas_a_csv.shape)
        
        pandas_a_csv.to_csv(self.output().path, index=False)
        
        
        engine = create_engine('postgresql+psycopg2://postgres:12345678@database-1.cqtrfcufxibu.us-west-2.rds.amazonaws.com:5432/dpa')
        print("ya pasó engine")
        table_name= 'metro'
        print(table_name)
        scheme='predict'
        print(scheme)
        pred.to_sql(table_name, con=engine,schema='predict' , if_exists='append')
        #df2.to_sql(table_name, con=engine,schema='semantic' , if_exists='replace')
#        connection.commit()
#        connection.close()
        
        #return prediction
    
    # Envía el output al S3 cop especificado con el nombre de output_path
    def output(self):
        output_path = "s3://dpaprojs3/predictionMetro_task_07_01/metro_{}.csv".format(self.date) #Formato del nombre para el json que entra al bucket S3
        print("en el output:",output_path)
        return luigi.contrib.s3.S3Target(path=output_path)




if __name__ == '__main__':
    luigi.predictionMetro()

