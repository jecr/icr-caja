# -*- coding: UTF-8 -*-
# Retoma usuarios previamente clasificados, genera csv
import json
import sys

rutaUsuarios = sys.argv[1]  # Lista de usuarios totales (con/sin descripción / existentes/no existentes)
rutaClasificados = sys.argv[2]  # Lista de usuarios existentes/con descripción clasificados

archivoUsuarios = open(rutaUsuarios, 'r')

archivoClasificados = open(rutaClasificados, 'r')
jsonClasificados = json.load(archivoClasificados)

archivoMedios = open('medios-historico.txt', 'r')
dictMedios = {}
for linea in archivoMedios:
    linea = linea.strip()
    dictMedios[linea] = ''

archivoPoliticos = open('politicos-historico.txt', 'r')
dictPoliticos = {}
for linea in archivoPoliticos:
    linea = linea.strip()
    dictPoliticos[linea] = ''

dictClasificados = {}
for item in jsonClasificados:
    dictClasificados[item['name']] = item['clasification']

dicFinal = {}
for linea in archivoUsuarios:
    linea = linea.strip()
    if linea in dictClasificados:
        dicFinal[linea] = dictClasificados[linea]
    if linea in dictMedios:
        dicFinal[linea] = 'medio'
    if linea in dictPoliticos:
        dicFinal[linea] = 'politico'
    if not linea in dictMedios and not linea in dictPoliticos and not linea in dictClasificados:
        dicFinal[linea] = 'ciudadano'

for caso in dicFinal:
    print caso + ',' + dicFinal[caso]
