# -*- coding: UTF-8 -*-
# Clasificador de usuarios
import json
from nltk.stem import SnowballStemmer
import re
import sys

# Asignación del stemmer en español
stemmer = SnowballStemmer("spanish")

rutaPoliticos = sys.argv[1]  # Archivo de terminos de políticos
rutaMedios = sys.argv[2]  # Archivo de términos de medios
rutaUsuarios = sys.argv[3]  # Archivo de lista de usuarios con descripción

# ==========================================
# ===== DICCIONARIOS DE PROBABILIDADES =====
# ==========================================

archivoPoliticos = open(rutaPoliticos, 'r')
jsonPoliticos = json.load(archivoPoliticos)

dictPolitico = {}
for item in jsonPoliticos:
    dictPolitico[item['palabra']] = item['porcentaje']

archivoMedios = open(rutaMedios, 'r')
jsonMedios = json.load(archivoMedios)

dictMedios = {}
for item in jsonMedios:
    dictMedios[item['palabra']] = item['porcentaje']

# ===================================
# ===== DICCIONARIO DE USUARIOS =====
# ===================================

archivoUsuarios = open(rutaUsuarios, 'r')
jsonUsuarios = json.load(archivoUsuarios)

# Creación de un diccionario con nombres de usuario como keys y descripciones como valores
listaUsuarios = {}
for linea in jsonUsuarios:
    listaUsuarios[linea['name']] = linea['description'].encode('UTF-8')

# ===================================
# ===== INICIO DE NORMALIZACIÓN =====
# ===================================

# Creo un diccionario de stopwords a partir de un archivo ubicado en el mismo directorio del script
stopwords = {}
archivoStop = open('stopwords.txt', 'r')
for stopw in archivoStop:
    stopwords[stopw.strip()] = ''

# Para el reemplazo de acentos por sus equivalentes no acentuadas
acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u'}

# Recorrido del listado de descripciones
for item in listaUsuarios:
    transform = listaUsuarios[item].strip()  # Elimino leading y trailing spaces
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
    listaUsuarios[item] = transform

# ================================
# ===== FIN DE NORMALIZACIÓN =====
# ================================
conteo = 0
clasificados = {}
for usuario in listaUsuarios:
    descrSplit = listaUsuarios[usuario].split()
    puntajeM = 0
    puntajeP = 0
    for item in descrSplit:
        if item in dictMedios:
            puntajeM += dictMedios[item]
        if item in dictPolitico:
            puntajeP += dictPolitico[item]
    if puntajeM > float(30) or puntajeP > float(30):
        if puntajeM > puntajeP:
            clasificados[usuario] = 'medio'
        else:
            clasificados[usuario] = 'politico'
    else:
        clasificados[usuario] = 'ciudadano'

listaClasificados = []
for itemClasif in clasificados:
    tempDict = {}
    tempDict['name'] = itemClasif
    tempDict['clasification'] = clasificados[itemClasif]
    listaClasificados.append(tempDict)

with open(rutaUsuarios.replace('recuperados', 'clasificados'), 'w') as f:
    json.dump(listaClasificados, f, indent=4, ensure_ascii=False)
