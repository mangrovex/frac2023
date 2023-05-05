import os
import shutil
import sqlite3

name = None
directorio = None
imagenes = None
nueva_imagen = None
fname = None
lname = None
fullname = None
current_directorio = os.getcwd()
traindirectorio = '/home/mvega/Development/frac/cvservice/knn_images/train/'
dirimagen = '/home/mvega/Development/frac/webservice/server/node-server/public/profile/'
pathdb = '/home/mvega/Development/frac/webservice/server/node-server/db/'
namedb = 'data.db'

# abro la conexion al sqlite
conn = sqlite3.connect('file:'+pathdb+namedb, uri=True)
c = conn.cursor()

# recorro el directorio
for x in os.listdir(traindirectorio):
	directorio = traindirectorio + x
	name = x.split('@')[0]
	fname = name[0]
	lname = name[1:]
	fullname = fname.capitalize() + ' ' + lname.capitalize()
	os.chdir(directorio)
	imagenes = os.listdir(directorio) 
	imagenes.sort()
	imagen = imagenes[0]
	#print (name, fullname, imagen)
	nombre_imagen = name + '.jpg'
	print(nombre_imagen)
	nueva_imagen = dirimagen + nombre_imagen
	shutil.copy(imagen, nueva_imagen)

	idname = (name,)
	c.execute('select * from profile where id=?', idname)

	if c.fetchone() is not None:
		print('existe')
		idparam = name
		imageparam = nombre_imagen
		conn.execute('update profile set image=? where id=?', (imageparam, idparam))
	else:
		print('no existe')
		idparam = name
		nameparam = fullname
		clearancetypeparam = 'A'
		imageparam = nombre_imagen
		conn.execute('insert into profile(id, name, clearancetype, image) values (?, ?, ?, ?)', (idparam, fullname, clearancetypeparam, imageparam))
	#break

c.close()
conn.commit()
conn.close()
