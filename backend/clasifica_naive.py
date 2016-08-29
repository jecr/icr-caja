# -*- coding: UTF-8 -*-
# Clasificador con Naive Bayes incorporado, archivos usados: stopwords.txt, clasificador.pickle, politicos-historico.txt, medios-historico.txt, politicos-historico-recuperados.json, medios-historico-recuperados.json
# Argumento 1 : Lista de usuarios recuperados ()
# Argumento 2 : Lista de usuarios totales
import json
from nltk.stem import SnowballStemmer
import os
import pickle
import re
import sys
from textblob.classifiers import NaiveBayesClassifier

# ============ UTILIDADES ==============

# Asignación del stemmer en español
stemmer = SnowballStemmer("spanish")

# Creo un diccionario de stopwords a partir de un archivo ubicado en el mismo directorio del script
stopwords = {}
archivoStop = open('util/stopwords.txt', 'r')
for stopw in archivoStop:
    stopwords[stopw.strip()] = ''

# Para el reemplazo de acentos por sus equivalentes no acentuadas
acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u'}

# =======================================
# ============ NORMALIZACIÓN ============
# =======================================


def textNormalization(dictUsuarios):

    # Contenedor de elementos normalizados
    normalizados = {}

    # Recorrido del diccionario de descripciones de usuarios
    for recListado in dictUsuarios:
        transform = dictUsuarios[recListado].strip()  # Elimino leading y trailing spaces
        transform = transform.lower()  # Cambio a minúsculas

        # Remoción de URLs
        URLless_string = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', transform)
        transform = URLless_string

        # Reemplazo de separadores (arbitrario)
        transform = transform.replace('/', ' ').replace('-', ' ')

        # Reemplazo de acentos
        for acento in acentos:
            transform = transform.replace(acento, acentos[acento])

        # Remoción de caracteres no alfabéticos
        for caracter in transform:
            if not caracter.isalpha() and not caracter == ' ':
                transform = transform.replace(caracter, '')

        # División de la cadena de texto para hacer un recorrido y eliminar stopwords
        transform = transform.split()
        for palabra in transform:
            if palabra in stopwords:
                transform[transform.index(palabra)] = ''  # Si la palabra se encuentra en el diccionario de stopwords, se elimina

        # Stemming: empleando el SnowballStemmer ubica la raíz de la palabra para eliminar plurales y otras transformaciones:
        for palabra in transform:
            transform[transform.index(palabra)] = stemmer.stem(palabra)
        transform = list(set(transform))  # Elimina palabras duplicadas de la lista
        transform = ' '.join(transform)  # Fusión de la cadena
        transform = ' '.join(transform.split())  # Separación - fusión para remover espacios de más
        if transform != '':
            normalizados[recListado] = transform

    return normalizados

if os.path.isfile('util/clasificador.pickle'):
    print('Clasificador ya entrenado, cargando...')
    f = open('util/clasificador.pickle', 'rb')
    clasificador = pickle.load(f)
    f.close()
    print('Clasificador cargado :D')
else:
    # ================================================
    # ============ CARGA DE DESCRIPCIONES ============
    # ================================================
    print('Clasificador no entrenado, entrenando (may take a while)...\nCargando archivos necesarios...\nNormalizando descripciones...')

    polRuta = 'util/politicos-historico-recuperados.json'  # Archivo de políticos (descripciones)
    medRuta = 'util/medios-historico-recuperados.json'  # Archivo de medios (descripciones)
    # ciuRuta = 'util/ciudadanos-historico-recuperados.json'  # Archivo de ciudadanos (descripciones)

    polArchivo = open(polRuta, 'r')
    politJson = json.load(polArchivo)

    medArchivo = open(medRuta, 'r')
    mediosJson = json.load(medArchivo)

    # ciuArchivo = open(ciuRuta, 'r')
    # ciudadJson = json.load(ciuArchivo)

    # Creación de un diccionario con nombres de usuario como keys y descripciones como valores
    polDescripciones = {}
    for linea in politJson:
        polDescripciones[linea['name']] = linea['description'].encode('UTF-8')

    medDescripciones = {}
    for linea in mediosJson:
        medDescripciones[linea['name']] = linea['description'].encode('UTF-8')

    # ciuDescripciones = {}
    # for linea in ciudadJson:
    #     ciuDescripciones[linea['name']] = linea['description'].encode('UTF-8')

    # Creación de diccionarios de usuarios = descipciones_normalizadas
    polNormalizados = textNormalization(polDescripciones)
    medNormalizados = textNormalization(medDescripciones)
    # ciuNormalizados = textNormalization(ciuDescripciones)
    print('Descripciones normalizadas.\nEntrenando clasificador...')
    # ============ Entrenamiento ============
    training = []
    for recNormalizados in polNormalizados:
        training.append((polNormalizados[recNormalizados], 'politico'))
    for recNormalizados in medNormalizados:
        training.append((medNormalizados[recNormalizados], 'medio'))
    # for recNormalizados in ciuNormalizados:
    #     training.append((ciuNormalizados[recNormalizados], 'ciudadano'))

    clasificador = NaiveBayesClassifier(training)
    f = open('util/clasificador.pickle', 'wb')
    pickle.dump(clasificador, f, -1)
    f.close()
    print('Clasificador entrenado :D\n')

print('\nNormalizando texto ingresado...')

porClasificar = {}
f = open(sys.argv[1], 'r')
classifyJson = json.load(f)
for item in classifyJson:
    porClasificar[item['name']] = item['description'].encode('UTF-8')

print('Texto normalizado.')

clasificaEsto = textNormalization(porClasificar)

# print clasificaEsto

fPolH = open('util/politicos-historico.txt', 'r')
historicos = {}
for item in fPolH:
    historicos[item.strip()] = 'politico'

fMedH = open('util/medios-historico.txt', 'r')
for item in fMedH:
    historicos[item.strip()] = 'medio'

print('\nClasificando:')
clasifSalida = {}
for item in clasificaEsto:
    if item in historicos:
        clasifSalida[item] = historicos[item]
    else:
        prob_dist = clasificador.prob_classify(clasificaEsto[item])
        if round(prob_dist.prob(prob_dist.max()), 3) == 1:
            clasifSalida[item] = prob_dist.max()
            # print item + ': ' + prob_dist.max() + ' --- Probabilidad: ' + str(round(prob_dist.prob(prob_dist.max()), 3))
        else:
            clasifSalida[item] = 'ciudadano'
            # print item + ': ciudadano --- Probabilidad opcional: ' + prob_dist.max() + ' con ' + str(round(prob_dist.prob(prob_dist.max()), 3))

print 'Leyendo lista completa de usuarios...'
fUserList = open(sys.argv[2], 'r')
for item in fUserList:
    item = item.strip()
    if not item in clasifSalida:
        if item in historicos:
            clasifSalida[item] = historicos[item]
        else:
            clasifSalida[item] = 'ciudadano'

print 'Imprimiendo salida...'
clasifExport = []
for item in clasifSalida:
    exportThis = {}
    exportThis['name'] = item
    exportThis['category'] = clasifSalida[item]
    clasifExport.append(exportThis)

# Escritura del archivo al terminar la ejecución
archivoRuta = sys.argv[2].split('.')
archivoRuta = archivoRuta[0] + '_clasifsalida.json'
with open(archivoRuta, 'w') as f:
    json.dump(clasifExport, f, indent=4, ensure_ascii=False)
