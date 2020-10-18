# -*- coding: utf-8 -*-
'''
El siguiente código toma la base de datos del SINAVE
y grafica el número de casos activos y el número de defunciones.
La base de datos que se usa como ejemplo está actualizada
al 14 de octubre.
direccion de descarga de los datos:
    https://www.gob.mx/salud/documentos/datos-abiertos-152127
'''

######### graficas covid: casos activos y defunciones ##########

# cargar librerias
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
# para cambiar formato de fecha de los axes
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime 
from datetime import timedelta
from scipy.stats import zscore

##### directorio
direc='F:/data/covid/sinave/14_oct/'
# nombre del archivo
df_n='201014COVID19MEXICO.csv'
#ruta completa
csv_file=direc+df_n
# donde se guardaran imagenes
dir_destino='F:/practicas_python/plotting/covid/'

##### cargamos base de datos
df_ini=pd.DataFrame()
contador=0
with open(csv_file,mode='r') as file:
    # Iterate over the file chunk by chunk
    for chunk in pd.read_csv(file,
                             chunksize=100000,  # chunksize=100 mil lineas
                             parse_dates=['FECHA_INGRESO']):
        contador+=1
        print('processing chunk:' + str(contador))
        df_ini=df_ini.append(chunk)

# trabajaremos con una copia de la base que le leyÃ³
df=df_ini.copy()

# analisis previo de la base cargada
df.info()
df.head()
df.tail()
df.shape
len(df['ID_REGISTRO'].unique())
df.iloc[0,32]
df.columns

# guardamos la fecha de la base de datos
fecha_actualizacion=str(df['FECHA_ACTUALIZACION'][0])

# convetir fechas a formato datetime
df[['FECHA_ACTUALIZACION','FECHA_INGRESO','FECHA_SINTOMAS',
    'FECHA_DEF']].head()

FECHAS=['FECHA_ACTUALIZACION','FECHA_INGRESO','FECHA_SINTOMAS',
    'FECHA_DEF']
for f in FECHAS:
    df[f]=pd.to_datetime(df[f],
  format='%Y-%m-%d',errors='coerce')

df[['FECHA_ACTUALIZACION','FECHA_INGRESO','FECHA_SINTOMAS',
    'FECHA_DEF']].head()
type(df['FECHA_ACTUALIZACION'][0])
df['FECHA_INGRESO'].dt.year

# convertir nombre de variables a minusculas
df.columns=[i.lower() for i in df.columns]
df[['fecha_actualizacion','fecha_ingreso','fecha_sintomas',
    'fecha_def']].head()


################# casos activos ################

# filtramos casos positivos
df['resultado_lab'].value_counts()
df_act=df.loc[df['resultado_lab']==1,:]
df_act.shape

# hacemos lista de todas las fechas disponibles
df['fecha_sintomas'].min()
fechas=list(df.sort_values('fecha_sintomas')['fecha_sintomas']\
            .unique())

# sÃ³lo nos interesa la fecha de sintomas
df_act.sort_values('fecha_sintomas',inplace=True)
df_act[['fecha_actualizacion','fecha_ingreso','fecha_sintomas',
    'fecha_def']].head()
df_act2=df_act[['fecha_actualizacion','fecha_sintomas']]

### contar numero de casos activos por fecha
df_act2['contador']=0
df_act2['fecha_ref']=pd.to_datetime('2020-01-01')
activos=[]
d = timedelta(days=14)
d0 = timedelta(days=0)
# creamos variables de dias de contagio
for fecha in fechas:
    df_act2['fecha_ref']=fecha
    # cuantos dÃ­as han pasado desde inicio de sintomas
    # con respecto a cada una de las fechas referencia
    df_act2['contador']=df_act2['fecha_ref']-df_act2['fecha_sintomas']
    # aislamos casos con menos de 14 dÃ­as desde inicio de sintomas
    activos_f=df_act2.loc[(df_act2['contador']<d) & 
                          (df_act2['contador']>=d0),'contador']
    # contamos numero de casos y lo registramos
    activos.append(len(activos_f))
    
# creamos dataframe con fecha y numero de casos activos
activos_df=pd.DataFrame(zip(fechas,activos))
activos_df.set_index(0,inplace=True)

# hacemos ajustes a la base de datos para poder graficar
fecha_corte='2020-09-30' # los registros de las ultimas dos semanas no estan actualizados
activos_df2=activos_df.loc['2020-02-01':fecha_corte,:]
activos_df2.columns=['activos']
activos_df2.index.name='fecha'
activos_df2['activos_miles']=activos_df2['activos']/1000

num_max=activos_df2['activos_miles'].max()
fecha_max = activos_df2[activos_df2['activos_miles']==num_max]\
    .reset_index()['fecha'][0].strftime("%Y-%m-%d")

#### graficamos casos activos por fecha
sns.set_style('whitegrid')
sns.set_context('paper')
fig, ax = plt.subplots()
ax.plot(activos_df2.index,activos_df2['activos_miles'],
        linestyle='-')
# colocamos texto y flecha
ax.annotate(str(num_max),xytext=[pd.Timestamp('2020-05-01'),num_max-2],
            xy=(pd.Timestamp(fecha_max),num_max),
            arrowprops={'arrowstyle':'->','color':'gray'})
# formato de las fechas
myFmt = mdates.DateFormatter('%b')
ax.xaxis.set_major_formatter(myFmt)
plt.xticks(rotation=45)
# Remove the spines
sns.despine(top=False,right=True)
# etiquetas y nota 
ax.set_xlabel('Fecha')
ax.set_ylabel('Miles de casos')
ax.set_title('Casos Activos COVID-19')
plt.figtext(0.33, -0.20, "ElaboraciÃ³n propia con datos del SINAVE \n datos al {}".format(fecha_actualizacion), ha="center", fontsize=8)
plt.show()
# Set figure dimensions and save as a PNG
fig.set_size_inches([5,3])
fig.savefig(dir_destino + 'casos_activos.png',
            dpi = 300, bbox_inches = 'tight')


################# defunciones  ##########################

# filtramos defunciones
df['resultado_lab'].value_counts()
condi= (df['resultado_lab']==1) & (~df['fecha_def'].isna())
df_def=df.loc[condi,:]
df_def.shape

# hacemos lista de todas las fechas disponibles
df['fecha_sintomas'].min()
fechas=list(df.sort_values('fecha_sintomas')['fecha_sintomas']\
            .unique())

# sÃ³lo nos interesa la fecha de defuncion
df_def.sort_values('fecha_def',inplace=True)
df_def[['fecha_actualizacion','fecha_ingreso','fecha_sintomas',
    'fecha_def']].head()
df_def2=df_def[['fecha_actualizacion','fecha_def']]

### contar numero de casos recuperados por fecha
df_def2['fecha_ref']=pd.to_datetime('2020-01-01')
defun=[]
# creamos variables de dias de contagio
for fecha in fechas:
    df_def2['fecha_ref']=fecha
    # defunciones por fecha
    defun_f=df_def2.loc[df_def2['fecha_def']==df_def2['fecha_ref'], :]
    # contamos numero de casos y lo registramos
    defun.append(len(defun_f))

# creamos dataframe con fecha y numero de casos activos
defun_df=pd.DataFrame(zip(fechas,defun))
defun_df.set_index(0,inplace=True)

# hacemos ajustes a la base de datos para poder graficar
fecha_corte='2020-09-30' # los registros de las ultimas dos semanas no estan actualizados
defun_df2=defun_df.loc['2020-02-01':fecha_corte,:]
defun_df2.columns=['defunciones']
defun_df2.index.name='fecha'

num_max=defun_df2['defunciones'].max()
fecha_max = defun_df2[defun_df2['defunciones']==num_max]\
    .reset_index()['fecha'][0].strftime("%Y-%m-%d")
    
#### graficamos casos recuperados acumulados por fecha
sns.set_style('whitegrid')
sns.set_context('paper')
fig, ax = plt.subplots()
ax.plot(defun_df2.index,defun_df2['defunciones'],
        linestyle='-')
# agregamos texto y flecha
ax.annotate(str(num_max),xytext=[pd.Timestamp('2020-05-15'),num_max-9],
            xy=(pd.Timestamp(fecha_max),num_max),
            arrowprops={'arrowstyle':'->','color':'gray'})
# formato de las fechas
myFmt = mdates.DateFormatter('%b')
ax.xaxis.set_major_formatter(myFmt)
plt.xticks(rotation=45)
# Remove the spines
sns.despine(top=False,right=True)
# etiquetas y nota al pie
ax.set_xlabel('Fecha')
ax.set_ylabel('Miles de casos')
ax.set_title('Defunciones COVID-19')
plt.figtext(0.33, -0.20, "ElaboraciÃ³n propia con datos del SINAVE \n datos al {}".format(fecha_actualizacion), ha="center", fontsize=8)
plt.show()
# Set figure dimensions and save as a PNG
fig.set_size_inches([5,3])
fig.savefig(dir_destino + 'defunciones2.png',
            dpi = 300, bbox_inches = 'tight')