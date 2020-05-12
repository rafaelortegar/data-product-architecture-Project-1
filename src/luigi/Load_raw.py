import json
import luigi
import datetime
from luigi.contrib.postgres import CopyToTable

import pandas as pd


class copyToPostgres2(CopyToTable):
    """
    Esta funcion inserta los datos raw del s3
    """

    #==============================================================================================================
    # Parameters
    #==============================================================================================================
    task_name = 'load_task_03_01'
    date = luigi.DateParameter(default=datetime.date.today())
    bucket = luigi.Parameter(default='dpaprojs3')
    #==============================================================================================================



    #==============================================================================================================
    # Credenciales de acceso a la base de datos
    #==============================================================================================================
    print("Iniciando conexión a la S3 de datos...")
    creds = pd.read_csv("../../credentials_postgres.csv")
    creds_aws = pd.read_csv("../../credentials.csv")
    print("credenciales leídas correctamente")
    #==============================================================================================================
    
    
    
    #==============================================================================================================
    # Se inicializan los parámetros para la conexión a la bd
    #============================================================================================================== 
    user = creds.user[0]
    password = creds.password[0]
    database = creds.db[0]
    host = creds.host[0]
    #nombre de la tabla donde vamos a insertar
    table = 'raw.metro'
    #estructura de las columnas de la tabla
    columns=   [("fecha","TEXT"),
                ("ano","TEXT"),
                ("linea","TEXT"),
                ("estacion","TEXT"),
                ("afluencia","TEXT")]
    #==============================================================================================================


    
                
    file_to_read = 'extractToJson_task_01/metro_' + self.date + '.json'
    # Conexión a la S3
    print("Iniciando la conexión con el recurso S3 que contiene los datos extraídos...")
    ses = boto3.session.Session(profile_name='rafael-dpa-proj') #, region_name='us-west-2') # Pasamos los parámetros apra la creación del recurso S3 (bucket) al que se va a conectar
    s3_resource = ses.resource('s3') # Inicialzamos e recursoS3
    dev_s3_client = ses.client('s3')
    obj = s3_resource.Bucket(self.bucket) # Metemos el bucket S3 en una variable obj
    print("Conexión Exitosa! :)")
        
    f = pd.DataFrame(columns=["fecha", "ano", "linea", "estacion", "afluencia"])
#
#        for i in range(len(json_content['records'])):
#            a_row = pd.Series(
#                [json_content['records'][i]["fields"]["fecha"], json_content['records'][i]["fields"]["anio"],
#                 json_content['records'][i]["fields"]["linea"], json_content['records'][i]["fields"]["estacion"],
#                 int(json_content['records'][i]["fields"]["afluencia"])])
#            row_df = pd.DataFrame([a_row])
#            row_df.columns = ["fecha", "anio", "linea", "estacion", "afluencia"]
#            df = pd.concat([df, row_df], ignore_index=True)