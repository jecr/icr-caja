# -*- coding: UTF-8 -*-
# =======================================
# ====== CLASIFICACIÓN DE USUARIOS ======
# =======================================

import json
import re
import pickle
import os
from nltk.stem import SnowballStemmer
from textblob.classifiers import NaiveBayesClassifier

# ============== UTILIDADES ================


# Asignación del stemmer en español
stemmer = SnowballStemmer("spanish")

# Creo un diccionario de stopwords a partir de un archivo ubicado en directorio util
stopwords = {}
archivoStop = open('util/stopwords.txt', 'r')
for stopw in archivoStop:
    stopwords[stopw.strip()] = ''

# Para el reemplazo de acentos por sus equivalentes no acentuadas
acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
           'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u'}

# =============================================================
# ============ NORMALIZACIÓN DE LISTAS DE USUARIOS ============
# =============================================================


def textNormalization(dictUsuarios):

    # Contenedor de elementos normalizados
    normalizados = {}

    # Recorrido del diccionario de descripciones de usuarios
    for recListado in dictUsuarios:
        transform = dictUsuarios[recListado]

        transform = singleNormalisation(transform)

        if transform != '':
            normalizados[recListado] = transform

    return normalizados


def singleNormalisation(texto):
    # Elimino leading y trailing spaces & cambio a minúsculas
    texto = texto.strip().lower()

    # Remoción de URLs
    URLless_string = re.sub(
        r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', texto)
    texto = URLless_string

    # Reemplazo de separadores (arbitrario)
    texto = texto.replace('/', ' ').replace('-', ' ')

    # Reemplazo de acentos
    for acento in acentos:
        texto = texto.replace(acento, acentos[acento])

    # Remoción de caracteres no alfabéticos
    for caracter in texto:
        if not caracter.isalpha() and not caracter == ' ':
            texto = texto.replace(caracter, '')

    # División de la cadena de texto para hacer un recorrido y eliminar stopwords
    texto = texto.split()
    for palabra in texto:
        if palabra in stopwords:
            # Si la palabra se encuentra en el diccionario de stopwords, se elimina
            texto[texto.index(palabra)] = ''

    # Stemming: empleando el SnowballStemmer ubica la raíz de la palabra para eliminar plurales y otras transformaciones:
    for palabra in texto:
        texto[texto.index(palabra)] = stemmer.stem(palabra)
    texto = list(set(texto))  # Elimina palabras duplicadas de la lista
    texto = ' '.join(texto)  # Fusión de la cadena
    # Separación - fusión para remover espacios de más
    texto = ' '.join(texto.split())

    return texto

# ===========================================
# ====== ENTRENAMIENTO DE CLASIFICADOR ======
# ===========================================


if os.path.isfile('util/clasificador.pickle'):
    print('Clasificador ya entrenado, cargando...')
    f = open('util/clasificador.pickle', 'rb')
    clasificador = pickle.load(f)
    f.close()
    print('Clasificador cargado :D')
else:
    # =============================================================
    # ============ CARGA DE DESCRIPCIONES DE HISTÓRICO ============
    # =============================================================
    print('Clasificador no entrenado, entrenando (may take a while)...\nCargando archivos necesarios...')

    # Archivo de políticos (descripciones)
    polRuta = 'util/politicos-historico-recuperados.json'
    # Archivo de medios (descripciones)
    medRuta = 'util/medios-historico-recuperados.json'

    polArchivo = open(polRuta, 'r')
    politJson = json.load(polArchivo)

    medArchivo = open(medRuta, 'r')
    mediosJson = json.load(medArchivo)

    # Creación de un diccionario con nombres de usuario como keys y descripciones como valores
    polDescripciones = {}
    for linea in politJson:
        polDescripciones[linea['name']] = linea['description'].encode('UTF-8')

    medDescripciones = {}
    for linea in mediosJson:
        medDescripciones[linea['name']] = linea['description'].encode('UTF-8')

    print('Normalizando descripciones...')

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

# ========================================================
# ====== CARGA DE ARCHIVO HISTÓRICO PRE-CLASIFICADO ======
# ========================================================

historicos = {}
fPolH = open('util/politicos-historico.txt', 'r')
for item in fPolH:
    historicos[item.strip()] = 'politico'

fMedH = open('util/medios-historico.txt', 'r')
for item in fMedH:
    historicos[item.strip()] = 'medio'

print 'Histórico pre-clasificado cargado'

# ==============================================================
# ====== CLASIFICACIÓN DE USUARIO ÚNICO (UNA DESCRIPCIÓN) ======
# ==============================================================


def clasifica(userMeta):
    clasifSalida = {}
    if userMeta['handler'] in historicos:
        clasifSalida['clase'] = historicos[userMeta['handler']]
    else:
        prob_dist = clasificador.prob_classify(
            singleNormalisation(userMeta['description']))
        if round(prob_dist.prob(prob_dist.max()), 3) == 1:
            clasifSalida['clase'] = prob_dist.max()
        else:
            clasifSalida['clase'] = 'ciudadano'

    return clasifSalida['clase']
