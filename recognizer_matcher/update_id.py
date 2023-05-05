import os
import shutil
import sqlite3
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

name = None
directorio = None
imagenes = None
nueva_imagen = None
fname = None
lname = None
fullname = None
row = None
current_directorio = os.getcwd()
traindirectorio = '/home/cramirez/Development/frac/cvservice/train/test_data/'
dirimagen = '/home/cramirez/Development/frac/webservice/server/node-server/public/profile/'
pathdb = '/home/cramirez/Development/frac/webservice/server/node-server/db/'
namedb = 'data.db'
dirfileid = '/home/cramirez/Development/'
namefileid = 'INFORMACION DE BIOMETRICO.xlsx'

df = pd.read_excel(dirfileid+namefileid, sheet_name='Hoja1', converters={'CCIEMPLEADO': str})
#print(df.columns)

os.chdir(traindirectorio)

for x in os.listdir(traindirectorio):
    if os.path.isdir(x):
        #print(x)
        # Find a row by a value in dataframe
        row = df.loc[df['Email']==x, 'CCIEMPLEADO']

        if not row.empty:
            cciempleado = row.item()
            #print(cciempleado)
            os.rename(x, cciempleado)

os.chdir(dirimagen)

for x in os.listdir(dirimagen):
    if os.path.isfile(x):
        #print(x)
        name = x.split('.')[0]
        row = df.loc[~df['Email'].isnull() & df['Email'].str.startswith(name), 'CCIEMPLEADO']
        
        if not row.empty:
            cciempleado = row.item() + '.jpg'
            #print(cciempleado)
            os.rename(x, cciempleado)

# abro la conexion al sqlite
conn = sqlite3.connect('file:'+pathdb+namedb, uri=True)
c = conn.cursor()

# Loop throught dataframe
for row in df.itertuples():
    #print(row.CCIEMPLEADO, row.Empleado, row.Ciudad, row.Email)
    if not pd.isnull(row.Email):
        print(row.Email)
        name = row.Email.split('@')[0]
        idname = (name,)
        c.execute('select * from profile where id=?', idname)

        if c.fetchone is not None:
            #print('Existe')
            idparam = row.CCIEMPLEADO
            nameparam = row.Empleado
            emailparam = row.Email
            imgparam = row.CCIEMPLEADO + '.jpg'
            #print(imgparam, idparam, emailparam, nameparam)
            conn.execute('update profile set id=?, name=?, email=?, image=? where id=?', (idparam, nameparam, emailparam, imgparam, name))

# cierro la conexion con sqlite
c.close()
conn.commit()
conn.close()

