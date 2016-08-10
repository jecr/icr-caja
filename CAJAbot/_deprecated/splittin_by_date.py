# -*- coding: UTF-8 -*-
import os
import sys
import json

archivo_tweets = sys.argv[1]
directorio = sys.argv[2]

# Comprueba la existencia del directorio
if not os.path.exists(directorio):
    print directorio + ' no existe, creando...'
    os.makedirs(directorio)
    print directorio + ' creado'
else:
    print "El directorio ya existe"

# Abre el archivo de tweets
lista_tweets = open(archivo_tweets)

# Crea una lista vacía para almacenar las líneas del archivo
lista_py = []

# Almacena las lineas del archivo dentro de la lista
for linea in lista_tweets:
    lista_py.append(linea)

total = len(lista_py)
cont = 0
previousDate = ''
dict_ids = {}

# Recorre la lista de publicaciones leyendo la fecha de creación
for element in lista_py:
    cont += 1
    print str(cont) + '/' + str(total),"           \r",

    currentJson = json.loads(element)
    currentDate = str(currentJson['created_at']).split(' ')[2] + str(currentJson['created_at']).split(' ')[1] + str(currentJson['created_at']).split(' ')[5]

    # Si el archivo no existe, lo crea
    dirVerif = directorio + '/' + directorio + '_' + currentDate + '.txt'
    if not os.path.isfile(dirVerif):

        # Intenta cerrar el archivo abierto, si lo hay
        try:
            currentFile.close()
        except Exception, e:
            pass

        print directorio + '_' + currentDate + ' no existe, creando...'
        currentFile = open(dirVerif, 'w')

        # Escribe la linea, luego cierra el archivo
        currentFile.write(element)
        currentFile.close()
        previousDate = currentDate
    else:
        if currentDate != previousDate:
            print 'Date switch: ' + currentDate

            # Intenta cerrar el archivo abierto, si lo hay
            try:
                currentFile.close()
            except Exception, e:
                pass

            # Abre el nuevo archivo para añadir la entrada
            currentFile = open(dirVerif, 'r+')

            # Crea el diccionario de ID's del archivo
            dict_ids = {}
            for linea in currentFile:
                currJsonIn = json.loads(linea)
                dict_ids[currJsonIn['id']] = ''

        # Comprueba la existencia del ID
        if not dict_ids.has_key(currentJson['id']):

            # Escribe la linea, luego cierra el archivo
            currentFile = open(dirVerif, 'a')
            currentFile.write(element)
        else:
            print 'Duplicado: ' + str(currentJson['id'])
        previousDate = currentDate
