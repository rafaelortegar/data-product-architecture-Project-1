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
import modelado

logger = logging.getLogger('luigi-interface')


class modelingMetro2(luigi.Task):
    """
    Function to train model from the mexico city metro data set on the database on postgres.
    It stores the metadata from uploading into the specified S3 bucket on AWS. Note: user MUST have the credentials 
    to use the aws s3 bucket.
    """

    #==============================================================================================================
    # Parameters
    #==============================================================================================================
    task_name = 'modelingMetro_task_06_01'
    date = luigi.Parameter()
    bucket = luigi.Parameter(default='dpaprojs3') # default='dpaprojs3')
    #==============================================================================================================
    
    # Indica que para iniciar loadCleaned proceso de carga de metadatos requiere que el task de extractToJson esté terminado
    def requires(self):
        return featureEngineering2(bucket=self.bucket, date=self.date) # , metadataCleaned(bucket = self.bucket, date=  self.date)

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
        connection = psycopg2.connect(user=creds.user[0],
                                  password=creds.password[0],
                                  host=creds.host[0],
                                  port=creds.port[0],
                                  database=creds.db[0])
        
        cursor = connection.cursor()
        
        # Leemos los datos de la RDS
        df = psql.read_sql('SELECT * FROM semantic.metro;', connection)
        print(df.shape) 
        
        # Hacemos el modelado
        modelos = modelado.ModelBuilder()
        print("modelos...",modelos)
        print("aqui ya hizo model builder")
        modelos = modelos.build_model(df)
        
        print("#...")
        print("##...")
        print("###...")
        print("####...")
        print("#####...")
        print("######...")
        print("Modelado completado!! :)")
        
#        # Escribe un JSON con la información descargada de la API, aqui esta el output
#        with self.output().open('w') as picklemodelo:
#            pickle.dump(modelos,file)
#        file = self.output().open('wb')
#        pickle.dump(modelos, file)
#        file.close()
#        
        with self.output().open('w') as output_file:
            pickle.dump(modelos,output_file)
        
        print("#...")
        print("##...")
        print("###...")
        print("####...")
        print("#####...")
        print("######...")
        print("Modelado completado!! :)")
        #connection = self.output().connect()
        #connection.autocommit = self.autocommit
        #cursor = connection.cursor()
        #sql = self.query
        
        ########################################################################        
        # commit and close connection
        cursor.close()
        connection.commit()
        connection.close()
        
    # Envía el output al S3 cop especificado con el nombre de output_path
    def output(self):
        output_path = "s3://dpaprojs3/modelingMetro_task_06_01/metro_{}.pkl". \
            format(self.date) #Formato del nombre para el json que entra al bucket S3
        return luigi.contrib.s3.S3Target(path=output_path)




if __name__ == '__main__':
    luigi.modelingMetro2()
############################################################### EMPEZAR MODELADO ###################################
#class modelingMetro(luigi.task):
#    """
#    Function to train model from the mexico city metro data set on the database on postgres.
#    It stores the metadata from uploading into the specified S3 bucket on AWS. Note: user MUST have the credentials 
#    to use the aws s3 bucket.
#    """
#
#    #==============================================================================================================
#    # Parameters
#    #==============================================================================================================
#    task_name = 'modelingMetro_task_06_01'
#    date = luigi.Parameter()
#    bucket = luigi.Parameter(default='dpaprojs3') # default='dpaprojs3')
#    #==============================================================================================================
#
#    # Indica que para iniciar el proceso de carga de metadatos requiere que emetadataloadl task de extractToJson esté terminado
#    def requires(self):
#        return featureEngineering(bucket=self.bucket, date=self.date), metadataFeatureEngineering(bucket=self.bucket, date=self.date)
#
#    
#    def run(self):
#
#        # Lee nuevamente el archivo JSON que se subió al S3 bucket, para después obtener metadatos sobre la carga
#        archivoquenosirve = 'feature_engineering_05_01/metro_' + self.date + '.csv'
#
#        creds = pd.read_csv("../../credentials_postgres.csv")
#        creds_aws = pd.read_csv("../../credentials.csv")
#        print("credenciales leídas correctamente")
#
#        # Conexión a la S3
#        print("Iniciando la conexión con el recurso S3 que contiene los datos extraídos...")
#        ses = boto3.session.Session(profile_name='rafael-dpa-proj') #, region_name='us-west-2') # Pasamos los parámetros apra la creación del recurso S3 (bucket) al que se va a conectar
#        s3_resource = ses.resource('s3') # Inicialzamos e recursoS3
#        obj = s3_resource.Bucket(self.bucket) # Metemos el bucket S3 en una variable obj
#        print("Conexión Exitosa! :)")
#
#        content_object = s3_resource.Object(self.bucket, archivoquenosirve)
#
#        #file_content = pd.read_csv(content_object) 
#        print("s3 encontrada exitosamente")
#
#
#        connection = psycopg2.connect(user=creds.user[0],
#                                          password=creds.password[0],
#                                          host=creds.host[0],
#                                          port=creds.port[0],
#                                          database=creds.db[0])
#
#
#        df = psql.read_sql('SELECT * FROM semantic.metro;', connection)
#
#
#        #dummies=pd.get_dummies(df["ano"],prefix='y')
#        #df=pd.concat([df,dummies],axis=1)
#        #dummies=pd.get_dummies(df["linea"],prefix='l')
#        #df=pd.concat([df,dummies],axis=1)
#        #print(df.columns)
#
#        print(df.shape)
#
#        #============== Modelado:
#        
#        modelos = modelado.ModelBuilder()
#        modelos = modelos.build_model(df)
#       
#        #sqlalchemy engine to psycopg2
#        #dialect+driver://username:password@host:port/database
#        engine = create_engine('postgresql+psycopg2://postgres:12345678@database-1.cqtrfcufxibu.us-west-2.rds.amazonaws.com:5432/dpa')
#        #user,password,host,port,db
#        #postgres,12345678,database-1.cqtrfcufxibu.us-west-2.rds.amazonaws.com,5432,dpa
#
#        table_name='semantic.metro'
#        scheme='semantic'
#        #df.to_sql(name="semantic.metro", con=engine, schema=scheme,if_exists='replace')
#        #print(psql.read_sql('SELECT * FROM semantic.metro LIMIT 10;', connection))
#        
#        #cursor.execute(text) #Execute a database operation (query or command).
#        
#        cursor = connection.cursor()
#        connection.commit() # This method sends a COMMIT statement to the MySQL server, committing the current transaction. 
#        cursor.close()# Close the cursor now (rather than whenever del is executed). The cursor will be unusable from this point forward
#        connection.close() # For a connection obtained from a connection pool, close() does not actually close it but returns it to the pool and makes it available for subsequent connection requests.
#
#
#
#        # para los outputs que no vamos a usar
#        vacio = ' '
#        data_vacia = {'vacio':[vacio]}
#        pandas_a_csv = pd.DataFrame(data=data_vacia)
#        pandas_a_csv.to_csv(self.output().path, index=False)
#        print("archivo creado correctamente")    
#
#=======
#        df2.to_sql("metro", engine, schema='semantic',if_exists='replace')
        

    
    # Envía el output al S3 bucket especificado con el nombre de output_path
#    def output(self):
#        output_path = "s3://{}/{}/metro_{}.csv". \
#            format(self.bucket, self.task_name, self.date) #Formato del nombre para el json que entra al bucket S3
#        return luigi.contrib.s3.S3Target(path=output_path)

##class SeparaBase(luigi.Task):
##    "Esta tarea separa la base en la Train & Test"
##
##    # Parametros del RDS
#    db_instance_id = luigi.Parameter()
#    db_name = luigi.Parameter()
#    db_user_name = luigi.Parameter()
#    db_user_password = luigi.Parameter()
#    subnet_group = luigi.Parameter()
#    security_group = luigi.Parameter()
#    # Parametros del Bucket
#    bucket = luigi.Parameter()
#    root_path = luigi.Parameter()
#
#    #Para la tarea actual
#    folder_path = '2.separacion_base'
#
#    def requires(self):
#        return PreprocesoBase(self.db_instance_id, self.db_name, self.db_user_name,
#                              self.db_user_password, self.subnet_group, self.security_group,
#                              self.bucket, self.root_path)
#
#
#    def run(self):
#
#        with self.input().open('r') as infile:
#             dataframe = pd.read_csv(infile, sep="\t")
#            #print('Pude leer el csv\n' , dataframe.head(5))
#            
#            
#            indice_ent = X['Fecha'] <= '2019-11-30'
#            
#            variables_a_eliminar = ['Fecha', 'Año', 'Afluencia']
#
#            x_mat = pd.get_dummies(X, columns = variables_categoricas, drop_first = True)
#        
#            x_ent = x_mat[indice_ent].drop(variables_a_eliminar, axis = 1)
#            x_pr = x_mat[~indice_ent].drop(variables_a_eliminar, axis = 1)
#            y_ent = categorias(x_mat['Afluencia'][indice_ent], 
#                           x_mat['Afluencia'][indice_ent])
#            y_pr = categorias(x_mat['Afluencia'][~indice_ent], 
#                          x_mat['Afluencia'][indice_ent])
#
#
#            vars_modelo = ['delegacion_inicio','mes','dia_semana','hora', 'tipo_entrada', 'incidente_c4_rec', 'target']
#            var_target = 'target'
#            [X_train, X_test, y_train, y_test] = funciones_mod.separa_train_y_test(dataframe, vars_modelo, var_target)
#
#            
#
#        
#
#
#       ses = boto3.session.Session(profile_name='default', region_name='us-east-1')
#       s3_resource = ses.resource('s3')
#       obj = s3_resource.Bucket(self.bucket)
#
#       with self.output()['x_ent'].open('w') as outfile1:
#            x_ent.to_csv(outfile1, sep='\t', encoding='utf-8', index=None)
#
#       with self.output()['x_pr'].open('w') as outfile2:
#            x_pr.to_csv(outfile2, sep='\t', encoding='utf-8', index=None)
#
#       with self.output()['y_ent'].open('w') as outfile3:
#            y_ent.to_csv(outfile3, sep='\t', encoding='utf-8', index=None)
#
#       with self.output()['y_pr'].open('w') as outfile4:
#            y_pr.to_csv(outfile4, sep='\t', encoding='utf-8', index=None)
#
##import os
##directorio = 'C:\\Users\\valen\\Documents\\Maestria-Data-Science\\Spring-2020\\MetodosGranEscala\\proyecto2\\data-product-architecture-Project\\modeloML'
##os.chdir(directorio)
##import luigi
##import numpy as np
##import pandas as pd
##from sklearn.impute import SimpleImputer
##from sklearn.linear_model import LogisticRegression
##from sklearn.metrics import confusion_matrix
##
##class MetroDataIngestion(luigi.Task):
##
##    def run(self):
##        X = pd.read_csv('afluencia-diaria-del-metro-cdmx.csv')
##        X.to_csv(self.output().path, index=False)
##
##    def output(self):
##        return luigi.LocalTarget("./Xtrain.csv")
##
###X = pd.read_csv('afluencia-diaria-del-metro-cdmx.csv')
##
##def rmse(y, pred):
##    return(np.sqrt(np.mean((y-pred)**2)))
##
##def categorias(x, y):
##    n = len(x)
##    z = np.array(x, dtype = str)    
##    q25 = np.quantile(y, 0.25)
##    q75 = np.quantile(y, 0.75)
##    z[x <= q25] = 'Bajo'
##    z[(x >= q25) & (x <= q75)] = 'Normal'
##    z[x >= q75] = 'Alto'
##    return(z)
##
##X['Fecha'] = pd.to_datetime(X['Fecha'])
##X['Dia'] = pd.DatetimeIndex(X['Fecha']).day.astype('object')
##X['Mes'] = pd.DatetimeIndex(X['Fecha']).month.astype('object')
##X['Dia_Semana'] = (pd.DatetimeIndex(X['Fecha']).weekday + 1).astype('object')
##
##indice_ent = X['Fecha'] <= '2019-11-30'
##
##variables_a_eliminar = ['Fecha', 'Año', 'Afluencia']
##
##variables_categoricas = X.dtypes.pipe(lambda x: x[x == 'object']).index
##
##num_cols = X.dtypes.pipe(lambda x: x[x != 'object']).index
##for x in num_cols:
##    imp = SimpleImputer(missing_values = np.nan, strategy = 'median')
##    imp.fit(np.array(X[x]).reshape(-1, 1))
##    X[x] = imp.transform(np.array(X[x]).reshape(-1, 1))
##
##nominal_cols = X.dtypes.pipe(lambda x: x[x == 'object']).index
##for x in nominal_cols:
##    imp = SimpleImputer(missing_values = np.nan, strategy = 'most_frequent')
##    imp.fit(np.array(X[x]).reshape(-1, 1))
##    X[x] = imp.transform(np.array(X[x]).reshape(-1, 1))
##
##x_mat = pd.get_dummies(X, columns = variables_categoricas, drop_first = True)
##
##x_ent = x_mat[indice_ent].drop(variables_a_eliminar, axis = 1)
##x_pr = x_mat[~indice_ent].drop(variables_a_eliminar, axis = 1)
##y_ent = categorias(x_mat['Afluencia'][indice_ent], 
##                   x_mat['Afluencia'][indice_ent])
##y_pr = categorias(x_mat['Afluencia'][~indice_ent], 
##                  x_mat['Afluencia'][indice_ent])
##
##def modelo_cat(cat, x_ent, y_ent, x_pr, y_pr, sc):
##
##    y_ent1 = np.where(y_ent == cat, 1, 0)
##    y_pr1 = np.where(y_pr == cat, 1, 0)
##luigi
##    modelo = LogisticRegression()
##    modelo.fit(x_ent, y_ent1)
##
##    pred = modelo.predict_proba(x_pr)[:,1]
##    prob = pred.copy()
##    pred = np.where(pred >= sc, 1, 0)
##    TP = np.sum((pred == 1) & (y_pr1 == 1))
##    TN = np.sum((pred == 0) & (y_pr1 == 0))
##    FP = np.sum((pred == 1) & (y_pr1 == 0))
##    FN = np.sum((pred == 0) & (y_pr1 == 1))
##
##    accuracy = (TP+TN)/(TP+TN+FP+FN)
##
##    precision = TP/(TP+FP)
##
##    recall = TP/(TP+FN)
##
##    a = {'modelo':modelo, 'pred':pred, 'prob':prob, 
##         'accuracy':accuracy, 'precision':precision, 'recall':recall}
##    return(a)
##
##cat = 'Bajo'
##sc = 0.56
##modelo = modelo_cat(cat, x_ent, y_ent, x_pr, y_pr, sc)
##
##modelo['accuracy']
##modelo['precision']
##modelo['recall']
##pred_bajo = modelo['pred']
##prob_bajo = modelo['prob']
##
##cat = 'Normal'
##sc = 0.50
##modelo = modelo_cat(cat, x_ent, y_ent, x_pr, y_pr, sc)
##
##modelo['accuracy']
##modelo['precision']
##modelo['recall']
##pred_normal = modelo['pred']
##prob_normal = modelo['prob']
##
##cat = 'Alto'
##sc = 0.50
##modelo = modelo_cat(cat, x_ent, y_ent, x_pr, y_pr, sc)
##
##modelo['accuracy']
##modelo['precision']
##modelo['recall']
##pred_alto = modelo['pred']
##prob_alto = modelo['prob']
##
##def pred_final(pred_bajo, prob_bajo, 
##               pred_normal, prob_normal, 
##               pred_alto, prob_alto):
##
##    n = len(pred_normal)
##    pred_final = np.array(pred_normal, dtype = str)
##    pred = pd.DataFrame({'Bajo':pred_bajo, 
##                         'Normal':pred_normal, 
##                         'Alto':pred_alto})
##    prob = pd.DataFrame({'Bajo':prob_bajo, 
##                         'Normal':prob_normal, 
##                         'Alto':prob_alto})
##    
##    for i in np.arange(1, n+1):
##        if pred.iloc[i-1, :].sum() == 1:
##            pred_final[i-1] = pred.iloc[i-1, :].idxmax()
##        else:
##            pred##    
##    return(pred_final)
##
##pred_f = pred_final(pred_bajo, prob_bajo, 
##               pred_normal, prob_normal, 
##               pred_alto, prob_alto)
##
##conf = pd.DataFrame(confusion_matrix(y_pr, pred_f), 
##                    index = ['real Bajo', 'real Normal', 'real Alto'], 
##                    columns = ['pred Bajo', 'pred Normal', 'pred Alto'])
##conf
##
##accuracy = np.sum(np.diag(conf))/np.sum(conf).sum()
##accuracy
##
#
#

#if __name__ == '__main__':
#    luigi.runAll()
    
    
    
