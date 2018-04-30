# -*- coding: UTF-8 -*-
import json
import os
import sys
import time
import webbrowser
import tweepy

import preprocesa
import clasificador
import localidades


# ===========================================
# ====== RECUPERACIÓN DE DESCRIPCIONES ======
# ===========================================


def recuperaUsuario(nombUsuario):
    print("Recuperando descripción faltante: " + nombUsuario)
    user = api.get_user(nombUsuario)
    recoveredUser = {}
    treatedText = user.description
    treatedText = treatedText.encode(
        'UTF-8').replace('\n', '').replace('\r', '')
    treatedText = ' '.join(treatedText.split())
    recoveredUser['description'] = treatedText
    treatedText = user.location
    treatedText = treatedText.encode(
        'UTF-8').replace('\n', '').replace('\r', '')
    treatedText = ' '.join(treatedText.split())
    recoveredUser['location'] = treatedText
    return recoveredUser


# VARIABLE PARA LA REANUDACIÓN DE EJECUCIÓN
execStatus = {}
execStatus['continue'] = 0


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
    if (actualIndex + 1) > (len(jsonClaves) - 1):
        print 'Se ha llegado a la última clave, reiniciando recorrido...'
        actualIndex = 0
    else:
        actualIndex = actualIndex + 1

    # Devuelve el índice actualizado
    return actualIndex


def conexion(actualIndex):  # Función de reconexión usando nueva clave
    # Re-asignación de variables para acceso
    # claveActual = jsonClaves[actualIndex]['name']
    consumer_key = jsonClaves[actualIndex]['c_k']
    consumer_secret = jsonClaves[actualIndex]['c_s']
    access_token = jsonClaves[actualIndex]['a_t']
    access_token_secret = jsonClaves[actualIndex]['a_ts']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Devuelve el objeto de claves para la conexión
    return (auth)


# Lectura del archivo de claves
archivoClaves = open('util/keys.json', 'r')
jsonClaves = json.load(archivoClaves)

claveActualIndex = -1  # Inicialización de clave de recuperación
# Genera un nuevo índice de clave
claveActualIndex = keySwitch(claveActualIndex)
api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave

# ==============================================
# === FIN DE INICIALIZACIÓN DE CLAVES DE API ===
# ==============================================

# python recupera.py "\"hoy no circula\" OR hoynocircula OR contingenciaambiental OR \"contingencia ambiental\" OR precontingencia" hoy_no_circula

# Selección de aplicación para recuperación
search_query = sys.argv[1]  # Término(s) de búsqueda
projectTweets = sys.argv[2]  # Nombre del proyecto
if len(sys.argv) == 4:  # URL raíz del proyecto
    urlRoot = sys.argv[3]
else:
    urlRoot = None
# minutero = sys.argv[3] # Tiempo de ejecuci1n = 1

if not os.path.isfile(projectTweets + '.prj'):
    currentFile = open(projectTweets + '.prj', 'w')

    # Escribe las líneas, luego cierra el archivo
    currentFile.write(search_query + '\n' + projectTweets)
    currentFile.close()  # Cierra el archivo tras la escritura

    # Abre el navegador en el administrador de proyectos
    print '\nArchivo de control creado: ' + search_query + '.prj'
    print '\nAbriendo listado de proyectos...'
    if urlRoot is not None:
        webbrowser.open(urlRoot + '/icr-caja/backend/')
else:
    # Abre el navegador en el administrador de proyectos
    print '\nAbriendo listado de proyectos...'
    if urlRoot is not None:
        webbrowser.open(urlRoot + '/icr-caja/backend/')

# Comprueba la existencia del directorio
if not os.path.exists(projectTweets):
    print '\n' + projectTweets + ' no existe, creando...'
    os.makedirs(projectTweets)
    print '\n' + projectTweets + ' creado'
else:
    print "\nEl proyecto ya existe"

savedDate = ''

# Inicializa el diccionario de IDs
dictIds = {}
currentFile = ''

continuable_file = {}
tweets_to_save = []
usrsAlmacenar = []
idsAlmacenadas = {}
handlersAlmacenados = {}

# =======================================
# ====== LISTAS, DICTS, DEFINITIOS ======
# =======================================

links_to_preprocess = []

# Fuentes de publicación confiables, para la reducción de bots
trustedSources = {}
trustedSources['<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>'] = ''
trustedSources['<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>'] = ''
trustedSources['<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>'] = ''
trustedSources[
    '<a href="https://mobile.twitter.com" rel="nofollow">Mobile Web (M5)</a>'] = ''
trustedSources['<a href="http://www.twitter.com" rel="nofollow">Twitter for Windows</a>'] = ''
trustedSources['<a href="http://www.twitter.com" rel="nofollow">Twitter for Windows Phone</a>'] = ''
trustedSources['<a href="http://twitter.com/#!/download/ipad" rel="nofollow">Twitter for iPad</a>'] = ''

# Para el reemplazo de acentos por sus equivalentes no acentuadas
acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
           'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u'}

execStart = time.time()

while (time.time() - execStart) < (60 * 999999999):
    try:
        for page in tweepy.Cursor(api.search, q=search_query, lang="es", count=100, include_entities=True).pages(100):
            # Procesamiento de tweets
            for tweet in page:
                cleanTweet = json.dumps(tweet._json)
                jsondTweet = json.loads(cleanTweet)  # Tweet parseado

                tweetStatus = {}

                # IDENTIFICACIÓN DE TIPO DE PUBLICACIÓN
                # RETWEET
                if 'retweeted_status' in jsondTweet:
                    if jsondTweet['user']['screen_name'].lower() != jsondTweet['retweeted_status']['user']['screen_name'].lower():
                        tweetStatus['rt'] = 1
                    else:
                        tweetStatus['rt'] = 0
                else:
                    tweetStatus['rt'] = 0

                # REPLY
                if jsondTweet['in_reply_to_status_id'] is not None and jsondTweet['user']['screen_name'].lower() != jsondTweet['in_reply_to_screen_name'].lower():
                    tweetStatus['rp'] = 1
                else:
                    tweetStatus['rp'] = 0

                # MENTION
                if jsondTweet['entities']['user_mentions'] != [] and 'retweeted_status' not in jsondTweet and jsondTweet['in_reply_to_status_id'] is None:
                    if len(jsondTweet['entities']['user_mentions']) == 1 and jsondTweet['entities']['user_mentions'][0]['screen_name'].lower() != jsondTweet['user']['screen_name'].lower():
                        tweetStatus['mn'] = 1
                    else:
                        tweetStatus['mn'] = 0
                else:
                    tweetStatus['mn'] = 0

                # Origen de la publicación
                origenPublicacion = jsondTweet['source'].encode('UTF-8')

                if origenPublicacion in trustedSources:
                    tweetStatus['ts'] = 1
                else:
                    tweetStatus['ts'] = 0

                # Localida de emisor
                emisor = {}
                if jsondTweet['user']['location'] is not None:
                    emisor['location'] = jsondTweet['user']['location'].encode(
                        'UTF-8').replace('\n', '').replace('\r', '')
                    emisor['location'] = ' '.join(emisor['location'].split())
                    emisor['location'] = emisor['location'].lower()
                    # Reemplazo de acentos
                    for acento in acentos:
                        emisor['location'] = emisor['location'].replace(
                            acento, acentos[acento])
                    for caracter in emisor['location']:
                        if not caracter.isalpha() and not caracter == ' ':
                            emisor['location'] = emisor['location'].replace(
                                caracter, '')
                    if emisor['location'] != '':
                        if localidades.locSimilarity(emisor['location']) != 0:
                            tweetStatus['loc'] = 1
                        else:
                            tweetStatus['loc'] = 0
                    else:
                        tweetStatus['loc'] = 1
                else:
                    tweetStatus['loc'] = 1

                # INTERACTION TYPE CHECK
                # Este paso incluye los filtros de interacción, plataforma de publicación y ubicación
                # Si aprueba la verificación, es guardado
                if (tweetStatus['rt'] == 1 or tweetStatus['rp'] == 1 or tweetStatus['mn'] == 1) and tweetStatus['ts'] == 1 and tweetStatus['loc'] == 1:

                    handlersList = []  # Lista para almacenar destinatarios y emisores

                    # Asignación de variables para la recueración de conversación
                    # toUser = jsondTweet['user']['screen_name'].lower()
                    # toUserStId = jsondTweet['id']

                    # Separa la fecha del archivo, la convierte en fecha por día
                    currentDate = str(jsondTweet['created_at']).split(' ')[1] + '-' + str(
                        jsondTweet['created_at']).split(' ')[2] + '-' + str(jsondTweet['created_at']).split(' ')[5]

                    # (ENTRADA) Si el archivo no existe, lo crea
                    dirVerif = projectTweets + '/' + projectTweets + \
                        '_' + currentDate + '(file_not_used).txt'
                    # NUEVOS ARCHIVOS (EN JSON)
                    archivoTweets = projectTweets + '/' + projectTweets + '_' + currentDate + '.json'
                    archivoViz = projectTweets + '/' + projectTweets + '_network_vis.json'

                    # RE-ARRANGEMENT OF METADATA
                    # Metadatos para cada tweet
                    meta_tweet = {}
                    meta_screen_name = jsondTweet['user']['screen_name'].lower().encode(
                        'UTF-8').replace('\n', '').replace('\r', '')
                    meta_screen_name = ' '.join(meta_screen_name.split())

                    meta_description = jsondTweet['user']['description'].encode(
                        'UTF-8')
                    meta_description = meta_description.replace(
                        '\n', '').replace('\r', '')
                    meta_description = ' '.join(meta_description.split())

                    meta_location = jsondTweet['user']['location'].encode(
                        'UTF-8').replace('\n', '').replace('\r', '')
                    meta_location = ' '.join(meta_location.split())

                    if tweetStatus['rt'] == 1:
                        meta_tweet['int_type'] = 'retweet'
                    if tweetStatus['rp'] == 1:
                        meta_tweet['int_type'] = 'reply'
                    if tweetStatus['mn'] == 1:
                        meta_tweet['int_type'] = 'mention'
                    
                    if 'retweeted_status' in jsondTweet:
                        if jsondTweet['retweeted_status']['user']['screen_name'] is not None:
                            meta_retweeted_status_handler = jsondTweet['retweeted_status']['user']['screen_name'].lower().encode('UTF-8').replace('\n', '').replace('\r', '')
                            meta_tweet['retweeted_status_handler'] = meta_retweeted_status_handler
                        else:
                            meta_tweet['retweeted_status_handler'] = 'empty'
                    else:
                        meta_tweet['retweeted_status_handler'] = 'empty'
                    if jsondTweet['in_reply_to_screen_name'] is not None:
                        meta_in_reply_to_screen_name = jsondTweet['in_reply_to_screen_name'].lower().encode('UTF-8').replace('\n', '').replace('\r', '')
                        meta_in_reply_to_screen_name = ' '.join(meta_in_reply_to_screen_name.split())
                        meta_tweet['in_reply_to_screen_name'] = meta_in_reply_to_screen_name
                    else:
                        meta_tweet['in_reply_to_screen_name'] = 'empty'
                    if jsondTweet['in_reply_to_status_id'] is not None:
                        meta_in_reply_to_status_id = jsondTweet['in_reply_to_status_id']
                        meta_tweet['in_reply_to_status_id'] = meta_in_reply_to_status_id
                    else:
                        meta_tweet['in_reply_to_status_id'] = 'empty'


                    meta_tweet['screen_name'] = meta_screen_name

                    meta_tweet['id'] = jsondTweet['id']

                    meta_tweet['source'] = origenPublicacion

                    meta_text = jsondTweet['text'].encode(
                        'UTF-8').replace('\n', '').replace('\r', '')
                    meta_text = ' '.join(meta_text.split())
                    meta_tweet['text'] = meta_text

                    if emisor['location'] != '' and emisor['location'] != 'empty':
                        meta_tweet['location'] = emisor['location']
                    else:
                        meta_tweet['location'] = 'empty'

                    if len(jsondTweet['entities']['user_mentions']) > 0:
                        meta_mentions_list = []
                        for item in jsondTweet['entities']['user_mentions']:
                            meta_mention = ''
                            meta_mention = item['screen_name'].lower().encode(
                                'UTF-8').replace('\n', '').replace('\r', '')
                            meta_mention = ' '.join(meta_mention.split())
                            meta_mentions_list.append(meta_mention)
                        meta_tweet['user_mentions'] = meta_mentions_list
                    else:
                        meta_tweet['user_mentions'] = 'empty'

                    meta_tweet['created_at'] = currentDate
                    # Fin de asignación de metadatos a meta_tweet

                    # Metadatos de emisor
                    emisor_meta = {}  # Metadatos para descripción de emisor
                    emisor_meta['handler'] = meta_screen_name
                    emisor_meta['description'] = meta_description
                    emisor_meta['location'] = meta_location
                    emisor_meta['class'] = clasificador.clasifica(emisor_meta)
                    handlersList.append(emisor_meta)

                    # Metadatos de destinatarios, por interacción
                    # RETWEET
                    destina_meta = {}
                    if meta_tweet['int_type'] == 'retweet':
                        destina_meta['handler'] = jsondTweet['retweeted_status']['user']['screen_name'].lower(
                        ).encode('UTF-8').replace('\n', '').replace('\r', '')
                        destina_meta['description'] = jsondTweet['retweeted_status']['user']['description'].encode(
                            'UTF-8').replace('\n', '').replace('\r', '')
                        # Separación - unión para remover espacios de más
                        destina_meta['description'] = ' '.join(
                            destina_meta['description'].split())
                        destina_meta['location'] = jsondTweet['retweeted_status']['user']['location'].encode(
                            'UTF-8').replace('\n', '').replace('\r', '')
                        # Separación - unión para remover espacios de más
                        destina_meta['location'] = ' '.join(
                            destina_meta['location'].split())
                        destina_meta['class'] = clasificador.clasifica(
                            destina_meta)
                        handlersList.append(destina_meta)
                    # REPLY
                    if meta_tweet['int_type'] == 'reply':
                        destina_meta['handler'] = jsondTweet['in_reply_to_screen_name'].lower().encode(
                            'UTF-8').replace('\n', '').replace('\r', '')
                        userMeta = recuperaUsuario(destina_meta['handler'])
                        destina_meta['description'] = userMeta['description']
                        destina_meta['location'] = userMeta['location']
                        destina_meta['class'] = clasificador.clasifica(
                            destina_meta)
                        handlersList.append(destina_meta)
                    # MENTION
                    if meta_tweet['int_type'] == 'mention':
                        for item in jsondTweet['entities']['user_mentions']:
                            destina_meta['handler'] = item['screen_name'].lower().encode(
                                'UTF-8').replace('\n', '').replace('\r', '')
                            userMeta = recuperaUsuario(destina_meta['handler'])
                            destina_meta['description'] = userMeta['description']
                            destina_meta['location'] = userMeta['location']
                            destina_meta['class'] = clasificador.clasifica(
                                destina_meta)
                            handlersList.append(destina_meta)

                    # ENDS REARRANGEMENT

                    if os.path.isfile(archivoTweets):
                        if execStatus['continue'] == 0:
                            print("El archivo " + archivoTweets + " ya existe")
                            print("Bandera de reanudación cambiada a: " +
                                  str(execStatus['continue']))
                            fOpen = open(archivoTweets, 'r')
                            loaded_tweets_file = json.load(fOpen)

                            # Recorre y almacena tweets en dict
                            print("Recuperando datos de archivo preexistente...")
                            count_users = 0
                            for item in loaded_tweets_file['tweets']:
                                idsAlmacenadas[item['id']] = ''
                                item['text'] = item['text'].encode('UTF-8')
                                if not item['id'] in idsAlmacenadas:
                                    tweets_to_save.append(item)

                                # Genera metadatos de enlace
                                enlaceActual = {}
                                enlaceActual['source'] = item['screen_name']
                                # RETWEET
                                if item['int_type'] == 'retweet':
                                    item_handler = item["retweeted_status_handler"]
                                    # Asigna info de target y tipo de interacción
                                    enlaceActual['target'] = item_handler
                                    enlaceActual['interaction'] = item['int_type']
                                    enlaceActual[item['int_type']] = 1
                                    print("Enlace existente === " + "Tipo: " +
                                          enlaceActual['interaction'] + "---" + "Source: " + enlaceActual["source"] + " --- " + "Target: " + item_handler)
                                    links_to_preprocess.append(enlaceActual)
                                # REPLY
                                if item['int_type'] == 'reply':
                                    item_handler = item['in_reply_to_screen_name']
                                    # Asigna info de target y tipo de interacción
                                    enlaceActual['target'] = item_handler
                                    enlaceActual['interaction'] = item['int_type']
                                    enlaceActual[item['int_type']] = 1
                                    print("Enlace existente === " + "Tipo: " +
                                          enlaceActual['interaction'] + "---" + "Source: " + enlaceActual["source"] + " --- " + "Target: " + item_handler)
                                    links_to_preprocess.append(enlaceActual)
                                # MENTION
                                if item['int_type'] == 'mention':
                                    for mentioned_user in item['user_mentions']:
                                        item_handler = mentioned_user
                                        # Asigna info de target y tipo de interacción
                                        enlaceActual['target'] = item_handler
                                        enlaceActual['interaction'] = item['int_type']
                                        enlaceActual[item['int_type']] = 1
                                        print("Enlace existente === " + "Tipo: " +
                                              enlaceActual['interaction'] + "---" + "Source: " + enlaceActual["source"] + " --- " + "Target: " + item_handler)
                                        links_to_preprocess.append(
                                            enlaceActual)

                            # Recorre y almacena handlers en dict
                            for item in loaded_tweets_file['users']:
                                handlersAlmacenados[item['handler'].encode(
                                    'UTF-8')] = item['class']
                                item['description'] = item['description'].encode(
                                    'UTF-8')
                                item['location'] = item['location'].encode(
                                    'UTF-8')
                                usrsAlmacenar.append(item)
                                count_users = count_users + 1

                            print(str(len(links_to_preprocess)) +
                                  " interacciones recuperadas de archivos existentes.")
                            print("Usuarios pre-existentes:" + str(count_users))
                            execStatus['continue'] = 1
                            print("Bandera de reanudación: " +
                                  str(execStatus['continue']))
                    else:
                        execStatus['continue'] = 0
                        print("Bandera de reanudación: " +
                              str(execStatus['continue']))
                        print("Nuevo archivo: " + dirVerif)

                    # Verificación de pre-existencia (TWT)
                    if not meta_tweet['id'] in idsAlmacenadas and meta_tweet['created_at'] == currentDate:
                        tweets_to_save.append(meta_tweet)
                        idsAlmacenadas[meta_tweet['id']] = ''

                        # Genera el arreglo a exportar
                        continuable_file['tweets'] = tweets_to_save

                        # Genera metadatos de enlace
                        enlaceActual = {}
                        enlaceActual['source'] = emisor_meta['handler']
                        enlaceActual['target'] = destina_meta['handler']
                        enlaceActual['interaction'] = meta_tweet['int_type']
                        enlaceActual[meta_tweet['int_type']] = 1

                        # Añade la interacción a la lista de enlaces
                        links_to_preprocess.append(enlaceActual)
                        for item in handlersList:

                            # Verificación de pre-existencia (USR)
                            if not item['handler'] in handlersAlmacenados:
                                usrsAlmacenar.append(item)
                                handlersAlmacenados[item['handler']
                                                    ] = item['class']

                                # Genera el arreglo a exportar
                                continuable_file['users'] = usrsAlmacenar
                        with open(archivoTweets, 'w') as f:
                            json.dump(continuable_file, f,
                                      indent=4, ensure_ascii=False)

                        print("Interacciones en " + archivoViz +
                              " :" + str(len(links_to_preprocess)))
                        # Archivo para visualización:
                        with open(archivoViz, 'w') as f:
                            json.dump(preprocesa.preprocesa(
                                links_to_preprocess, handlersAlmacenados), f, indent=4, ensure_ascii=False)

                    # DEPRECATED (BUT STILL USEFUL !!!!!!!!!!!!!!!!!!!1)
                    if not os.path.isfile(dirVerif):

                        currentFile = open(dirVerif, 'w')

                        # Escribe la linea, luego cierra el archivo
                        currentFile.write(cleanTweet)
                        currentFile.write('\n')
                        dictIds[jsondTweet['id']] = ''

                        currentFile.close()  # Cierra el archivo tras la escritura
                    else:

                        # Si el archivo ya existe, comprueba la fecha actual
                        if currentDate != savedDate:

                            savedDate = currentDate
                            # Si el archivo existe, lo abre para lectura
                            currentFile = open(dirVerif, 'r')
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

                            currentFile.close()  # Cierra el archivo tras la escritura

            # Fin consulta de límite
            if consultasRestantes() < 1:
                # Genera un nuevo índice de clave
                print("Límite de consultas alcanzado, empleando nueva clave...")
                print("Clave actual: " + claveActualIndex)
                claveActualIndex = keySwitch(claveActualIndex)
                print("Clave a utilizar: " + claveActualIndex)
                # Conexión usando nueva clave
                api = tweepy.API(conexion(claveActualIndex))
                break
    except Exception, e:
        print e
        claveActualIndex = keySwitch(claveActualIndex)
        # Conexión usando nueva clave
        api = tweepy.API(conexion(claveActualIndex))

        if hasattr(e, 'response'):
            print e
            pass
        else:
            print e
            pass
