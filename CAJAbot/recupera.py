# -*- coding: UTF-8 -*-
import json
import os
import sys
import time
import tweepy

# ===========================================
# ====== RECUPERADOR DE CONVERSACIONES ======
# ===========================================

def getConversation(theUser, theUserTweetId, theApi):
    cadenaBusqueda = 'to:' + theUser
    try:
        for page in tweepy.Cursor(theApi.search, q=cadenaBusqueda, since_id=theUserTweetId, lang="es", include_entities=True, count=100).pages(10):
            for convTweet in page:
                prinTweet = json.dumps(convTweet._json)
                convTweet = json.loads(prinTweet)
                if convTweet['in_reply_to_status_id'] == theUserTweetId and not convTweet['id'] in dictIds:
                    currentFile.write(prinTweet)
                    currentFile.write('\n')
                    dictIds[convTweet['id']] = ''
                    print 'Primer nivel de conversación obtenido para: ' + theUser.encode('UTF-8')

                    # ONE LEVEL DOWN (The tweetception starts)
                    # Consigue el id del tweet actual, luego recupera el nombre de usuario
                    UNO_idUsuario = convTweet['user']['screen_name'].lower()
                    UNO_tuitId = convTweet['id']
                    UNO_subQuery = 'to:' + UNO_idUsuario
                    for UNO_subPage in tweepy.Cursor(theApi.search, q=UNO_subQuery, since_id=UNO_tuitId, lang="es", include_entities=True, count=100).pages(10):
                        for UNO_subTweet in UNO_subPage:
                            UNO_printSubTweet = json.dumps(UNO_subTweet._json)
                            UNO_subTweet = json.loads(UNO_printSubTweet)
                            if UNO_subTweet['in_reply_to_status_id'] == UNO_tuitId and not convTweet['id'] in dictIds:
                                currentFile.write(UNO_printSubTweet)
                                currentFile.write('\n')
                                dictIds[convTweet['id']] = ''
                                print 'Segundo nivel de conversación obtenido para: ' + theUser.encode('UTF-8')

    except Exception, e:
        if hasattr(e, 'response'):
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 429:
                    print '\nExcepción: Límite de solicitudes alcanzado'
                    return 'newKeyNeeded'
            else:
                print e.response
                return 'newKeyNeeded'
        else:
            print e
            print 'Exception attributes error'
            return 'newKeyNeeded' 

# ======================================================
# ====== ABREVIACIÓN DE CONSULTA DE LÍMITE DE API ======
# ======================================================

def consultasRestantes():
    # Consulta el límite restante de consultas
    data = api.rate_limit_status()
    remaining = data['resources']['users']['/users/show/:id']['remaining']
    return remaining

# =============================================
# ====== INICIALIZACIÓN DE CLAVES DE API ======
# =============================================


def keySwitch(actualIndex):  # Funcion para actualización de índice de clave
    print '\nAsignación de claves...'
    if (actualIndex + 1) > (len(jsonClaves) - 1):
        print 'Se ha llegado a la última clave, reiniciando recorrido...'
        actualIndex = 0
    else:
        actualIndex = actualIndex + 1

    # Devuelve el índice actualizado
    return actualIndex


def conexion(actualIndex):  # Función de reconexión usando nueva clave
    # Re-asignación de variables para acceso
    claveActual = jsonClaves[actualIndex]['name']
    consumer_key = jsonClaves[actualIndex]['c_k']
    consumer_secret = jsonClaves[actualIndex]['c_s']
    access_token = jsonClaves[actualIndex]['a_t']
    access_token_secret = jsonClaves[actualIndex]['a_ts']
    print 'Clave cargada: ' + claveActual + '\n'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Devuelve el objeto de claves para la conexión
    return (auth)

# Lectura del archivo de claves
archivoClaves = open('util/keys.json', 'r')
jsonClaves = json.load(archivoClaves)

claveActualIndex = -1  # Inicialización de clave de recuperación
claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave

# ==============================================
# === FIN DE INICIALIZACIÓN DE CLAVES DE API ===
# ==============================================

# python recover.py alfa "\"hoy no circula\" OR hoynocircula OR contingenciaambiental OR \"contingencia ambiental\" OR precontingencia" hoy_no_circula
# python recover.py bravo "panamapapers OR \"papeles de panama\"" panama_papers
# python recover.py charlie debateoaxaca2016 debate_oaxaca

# Selección de aplicación para recuperación
search_query = sys.argv[1]  # Término(s) de búsqueda
projectTweets = sys.argv[2]  # Nombre del proyecto

# Comprueba la existencia del directorio
if not os.path.exists(projectTweets):
    print '\n' + projectTweets + ' no existe, creando...'
    os.makedirs(projectTweets)
    print '\n' + projectTweets + ' creado'
else:
    print "\nEl directorio ya existe"

if not os.path.isfile(projectTweets + '/query.txt'):
    terminos = open(projectTweets + '/query.txt', 'w')
    search_query = search_query.replace('"','\\"')
    search_query = '"' + search_query + '" ' + projectTweets
    terminos.write(search_query)
    print 'Archivo de cadena de búsqueda creado.'
else:
    print 'Archivo de cadena de búsqueda existente.'

savedDate = ''

# Inicializa el diccionario de IDs
dictIds = {}
currentFile = ''

while 1 > 0:
    try:
        for page in tweepy.Cursor(api.search, q=search_query, lang="es", count=100, include_entities=True).pages(100):
            # Procesamiento de tweets
            for tweet in page:
                cleanTweet = json.dumps(tweet._json)
                jsondTweet = json.loads(cleanTweet)  # Tweet parseado

                # Asignación de variables para la recueración de conversación
                toUser = jsondTweet['user']['screen_name'].lower()
                toUserStId = jsondTweet['id']

                # Separa la fecha del archivo, la convierte en fecha por día
                currentDate = str(jsondTweet['created_at']).split(' ')[1] + str(jsondTweet['created_at']).split(' ')[2] + str(jsondTweet['created_at']).split(' ')[5]

                # Si el archivo no existe, lo crea
                dirVerif = projectTweets + '/' + projectTweets + '_' + currentDate + '.txt'

                if not os.path.isfile(dirVerif):
                    print projectTweets + '_' + currentDate + ' no existe, creando...'
                    currentFile = open(dirVerif, 'w')
                    print dirVerif + ' opened.'

                    # Escribe la linea, luego cierra el archivo
                    currentFile.write(cleanTweet)
                    currentFile.write('\n')
                    dictIds[jsondTweet['id']] = ''
                    # Recuperación de conversación sobre este tweet:
                    if getConversation(toUser, toUserStId, api) == 'newKeyNeeded':
                        claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
                        api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave
                    currentFile.close()  # Cierra el archivo tras la escritura
                else:

                    # Si el archivo ya existe, comprueba la fecha actual
                    if currentDate != savedDate:
                        print '\nFecha actual: ' + currentDate
                        savedDate = currentDate

                        # Si el archivo existe, lo abre para lectura
                        currentFile = open(dirVerif, 'r')
                        print dirVerif + ' opened.'

                        # Crea el diccionario de ID's del archivo
                        dictIds = {}
                        for linea in currentFile:
                            currJsonIn = json.loads(linea)
                            dictIds[currJsonIn['id']] = ''

                        currentFile.close()  # Cierra el archivo del cual creó el diccionario

                    # Comprueba la existencia del ID
                    if not jsondTweet['id'] in dictIds:
                        # Abre archivo para edición
                        currentFile = open(dirVerif, 'a')

                        # Escribe la linea, luego cierra el archivo
                        currentFile.write(cleanTweet)
                        currentFile.write('\n')
                        dictIds[jsondTweet['id']] = ''
                        # Recuperación de conversación sobre este tweet:
                        if getConversation(toUser, toUserStId, api) == 'newKeyNeeded':
                            claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
                            api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave
                        currentFile.close()  # Cierra el archivo tras la escritura
            
            # Fin consulta de límite
            if consultasRestantes() < 1:
                claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
                api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave
                break
    except Exception, e:
        if hasattr(e, 'response'):
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 429:
                    claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
                    api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave
            else:
                print e.response
                pass
        else:
            print e
            pass
