# -*- coding: UTF-8 -*-
# Contador de fecuencia de palabras
import json
from nltk.stem import SnowballStemmer
import re
import sys

# Asignación del stemmer en español
stemmer = SnowballStemmer("spanish")

archivoRuta = sys.argv[1]

archivo = open(archivoRuta, 'r')
archivoJson = json.load(archivo)

# Creo un diccionario de stopwords a partir de un archivo ubicado en el mismo directorio del script
stopwords = {}
archivoStop = open('stopwords.txt', 'r')
for stopw in archivoStop:
    stopwords[stopw.strip()] = ''

# Creación de un diccionario con nombres de usuario como keys y descripciones como valores
listado = {}
for linea in archivoJson:
    listado[linea['name']] = linea['description'].encode('UTF-8')

# Para el reemplazo de acentos por sus equivalentes no acentuadas
acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u'}

# Contenedor de elementos normalizados
normalizados = {}

# Recorrido del listado de descripciones
for item in listado:
    transform = listado[item].strip()  # Elimino leading y trailing spaces
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
    normalizados[item] = transform

# Diccionario de palabras en el archivo. Key = Palabra, Value = Conteo
palabrasArchivo = {}

# Por cada descripción normalizada, almacena cada palabra asignándole el número de repeticiones
# Sólo puede haber una aparición de la palabra por cuenta
for elemento in normalizados:
    cadenaSeparada = normalizados[elemento].split()  # Separa la descripción
    for palabra in cadenaSeparada:
        if palabra in palabrasArchivo:
            palabrasArchivo[palabra] += 1  # Si la palabra ya existe, aumenta en 1 el número de apariciones
        else:
            palabrasArchivo[palabra] = 1  # Si no existe aún, asigna un 1

# Número de cuentas ingresadas al script
cuentasTotales = len(listado)

# Almacena las palabras en una lista, luego las ordena
sortedKeys = []
for palabraContada in palabrasArchivo:
    sortedKeys.append(palabraContada)
sortedKeys.sort()

# La probabilidad de pertenencia es equivalente al porcentaje de cuentas en que aparece el término
# Número de apariciones / Cuentas totales * 100
# Ingresa los valores en orden alfabético a un arreglo multidimensional
listaPorcentajes = []
for word in sortedKeys:
    porcentajePalabra = {}
    probabilidad = (float(palabrasArchivo[word]) / float(cuentasTotales)) * 100
    porcentajePalabra['palabra'] = word
    porcentajePalabra['porcentaje'] = probabilidad
    listaPorcentajes.append(porcentajePalabra)


def getPercenteage(item):
    return item['porcentaje']

listaPorcentajes.sort(key=getPercenteage, reverse=True)

# Escritura del archivo al terminar la ejecución
with open(archivoRuta.replace('recuperados', 'frecuencia'), 'w') as f:
    json.dump(listaPorcentajes, f, indent=4, ensure_ascii=False)
