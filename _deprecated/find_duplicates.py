# -*- coding: UTF-8 -*-
import json
import sys

inputFile = sys.argv[1]  # Archivo a depurar

archivoAbierto = open(inputFile, 'r')
archivoSalida = open(inputFile + '-clean.txt', 'w')

lasIds = {}
lineastotales = 0

for linea in archivoAbierto:
    lineastotales += 1
    tuitLeido = json.loads(linea)
    if not lasIds.has_key(tuitLeido['id']):
        lasIds[tuitLeido['id']] = ''
        archivoSalida.write(linea)

print str(lineastotales - len(lasIds)) + ' duplicados'
