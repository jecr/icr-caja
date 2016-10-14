# -*- coding: UTF-8 -*-
import json
import os
import sys
import time
import tweepy

# ====================================================
# ====== SIMILITUD DE CADENAS, PARA LOCALIDADES ======
# ====================================================

archivoLugares = open('util/locationsmx.txt', 'r')
lugaresMx = {}
for item in archivoLugares:
    lugaresMx[item.strip()] = ''

def locSimilarity(thisLocation):
    if thisLocation in lugaresMx:
        return 1
    else:
        locSim = {}
        locSim['score'] = 0

        for item in lugaresMx:
            cadena = thisLocation
            comp = item
            coincide = ''
            minimo_coinc = 95

            similarity = {}

            if cadena == comp:
                similarity['score'] = 100
            else:
                start = 0
                end = 1
                needle = list(cadena)[0]
                while end < len(cadena) and start < len(cadena):
                    end = 1

                    while comp.find(needle) > -1:
                        end += 1;

                        if len(coincide) < len(needle):
                            coincide = needle
                            
                        desfase = 0
                        needle = ''
                        for item in range(start,start + end):
                            if (desfase + start) < len(cadena):
                                needle += list(cadena)[desfase + start]
                            else:
                                needle = 'null'
                            desfase += 1

                    start += 1
                    if start < len(cadena):
                        needle = list(cadena)[start]
                similarity['score'] = ( (len(coincide) * 100) / len(cadena) )

            if  similarity['score'] > minimo_coinc:
                locSim['score'] = similarity['score']

        if locSim['score'] != 0:
            return 1
        else:
            return 0

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
                    #!!! print 'Primer nivel de conversación obtenido para: ' + theUser.encode('UTF-8')

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
                                #!!! print 'Segundo nivel de conversación obtenido para: ' + theUser.encode('UTF-8')

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
    #!!! print '\nAsignación de claves...'
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
    #!!! print 'Clave cargada: ' + claveActual + '\n'

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

# python recupera.py "\"hoy no circula\" OR hoynocircula OR contingenciaambiental OR \"contingencia ambiental\" OR precontingencia" hoy_no_circula

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

savedDate = ''

# Inicializa el diccionario de IDs
dictIds = {}
currentFile = ''

usrHandlers = {}
currentUsrFile = ''

# Fuentes de publicación confiables, para la reducción de bots
trustedSources = {}
trustedSources['<a href="http://twitter.com/download/iphone" rel="nofollow">Twitter for iPhone</a>'] = ''
trustedSources['<a href="http://twitter.com/download/android" rel="nofollow">Twitter for Android</a>'] = ''
trustedSources['<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>'] = ''
trustedSources['<a href="https://mobile.twitter.com" rel="nofollow">Mobile Web (M5)</a>'] = ''
trustedSources['<a href="http://www.twitter.com" rel="nofollow">Twitter for Windows</a>'] = ''
trustedSources['<a href="http://www.twitter.com" rel="nofollow">Twitter for Windows Phone</a>'] = ''
trustedSources['<a href="http://twitter.com/#!/download/ipad" rel="nofollow">Twitter for iPad</a>'] = ''

execStart = time.time()

while (time.time() - execStart) < (60*10):
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
                    if jsondTweet['user']['screen_name'] != jsondTweet['retweeted_status']['user']['screen_name']:
                        tweetStatus['rt'] = 1
                    else:
                        tweetStatus['rt'] = 0
                else:
                    tweetStatus['rt'] = 0

                # REPLY
                if jsondTweet['in_reply_to_status_id'] != None and jsondTweet['user']['screen_name'] != jsondTweet['in_reply_to_screen_name']:
                    tweetStatus['rp'] = 1
                else:
                    tweetStatus['rp'] = 0

                # MENTION
                if jsondTweet['entities']['user_mentions'] != [] and not 'retweeted_status' in jsondTweet and jsondTweet['in_reply_to_status_id'] == None:
                    if len(jsondTweet['entities']['user_mentions']) == 1 and jsondTweet['entities']['user_mentions'][0]['screen_name'] != jsondTweet['user']['screen_name']:
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
                if jsondTweet['user']['location'] != None:
                    emisor['location'] = jsondTweet['user']['location'].encode('UTF-8').replace('\n', '').replace('\r', '')
                    emisor['location'] = ' '.join(emisor['location'].split())
                    emisor['location'] = emisor['location'].lower()
                    for caracter in emisor['location']:
                        if not caracter.isalpha() and not caracter == ' ':
                            emisor['location'] = emisor['location'].replace(caracter, '')
                    if emisor['location'] != '':
                        if locSimilarity(emisor['location']) != 0:
                            print emisor['location']
                            tweetStatus['loc'] = 1
                        else:
                            tweetStatus['loc'] = 0
                    else:
                        tweetStatus['loc'] = 1
                else:
                    tweetStatus['loc'] = 1

                # INTERACTION TYPE CHECK
                # Si aprueba la verificación, es guardado
                if (tweetStatus['rt'] == 1 or tweetStatus['rp'] == 1 or tweetStatus['mn'] == 1) and tweetStatus['ts'] == 1 and tweetStatus['loc'] == 1:

                    # Asignación de variables para la recueración de conversación
                    toUser = jsondTweet['user']['screen_name'].lower()
                    toUserStId = jsondTweet['id']

                    # Separa la fecha del archivo, la convierte en fecha por día
                    currentDate = str(jsondTweet['created_at']).split(' ')[1] + str(jsondTweet['created_at']).split(' ')[2] + str(jsondTweet['created_at']).split(' ')[5]

                    # (ENTRADA) Si el archivo no existe, lo crea
                    dirVerif = projectTweets + '/' + projectTweets + '_' + currentDate + '.txt'

                    # (USUARIOS) Si el archivo no existe, lo crea
                    usrDirVerif = projectTweets + '/' + projectTweets + '_' + currentDate + '_users.txt'
                    emisorDesc = jsondTweet['user']['description'].encode('UTF-8')
                    emisorDesc = emisorDesc.replace('\n', '').replace('\r', '')
                    emisorDesc = ' '.join(emisorDesc.split())  # Separación - unión para remover espacios de más
                    emisorName = jsondTweet['user']['screen_name'].encode('UTF-8').replace('\n', '').replace('\r', '')

                    # RE-ARRANGEMENT OF METADATA
                    meta_tweet = {}
                    meta_screen_name = jsondTweet['user']['screen_name'].encode('UTF-8').replace('\n', '').replace('\r', '')
                    meta_screen_name = ' '.join(meta_screen_name.split())
                    meta_tweet['screen_name'] = meta_screen_name

                    meta_tweet['id'] = jsondTweet['id']

                    if jsondTweet['in_reply_to_screen_name'] != None:
                        meta_in_reply_to_screen_name = jsondTweet['in_reply_to_screen_name'].encode('UTF-8').replace('\n', '').replace('\r', '')
                        meta_in_reply_to_screen_name = ' '.join(meta_in_reply_to_screen_name.split())
                        meta_tweet['in_reply_to_screen_name'] = meta_in_reply_to_screen_name
                    else:
                        meta_tweet['in_reply_to_screen_name'] = 'empty'

                    if jsondTweet['in_reply_to_status_id'] != None:
                        meta_in_reply_to_status_id = jsondTweet['in_reply_to_status_id']
                        meta_tweet['in_reply_to_status_id'] = meta_in_reply_to_status_id
                    else:
                        meta_tweet['in_reply_to_status_id'] = 'empty'
                    
                    meta_tweet['source'] = origenPublicacion

                    meta_text = jsondTweet['text'].encode('UTF-8').replace('\n', '').replace('\r', '')
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
                            meta_mention = item['screen_name'].encode('UTF-8').replace('\n', '').replace('\r', '')
                            meta_mention = ' '.join(meta_mention.split())
                            meta_mentions_list.append(meta_mention)
                        meta_tweet['user_mentions'] = meta_mentions_list
                    else:
                        meta_tweet['user_mentions'] = 'empty'
                    # ENDS REARRANGEMENT

                    # ENTRADA (COMBINAR CON REARRANGEMENT)
                    if not os.path.isfile(dirVerif):
                        
                        currentFile = open(dirVerif, 'w')
                        
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
                            
                            savedDate = currentDate
                            # Si el archivo existe, lo abre para lectura
                            currentFile = open(dirVerif, 'r')
                            # Crea el diccionario de ID's del archivo
                            dictIds = {}
                            for linea in currentFile:
                                currJsonIn = json.loads(linea)
                                dictIds[currJsonIn['id']] = ''
                            currentFile.close()  # Cierra el archivo del cual creó el diccionario

                            # Repite el proceso para el archivo de usuarios
                            currentUsrFile = open(usrDirVerif, 'r')
                            usrHandlers = {}
                            for linea in currentUsrFile:
                                usrHandlers[linea] = ''
                            currentUsrFile.close()

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

                    # LISTA DE USUARIOS
                    if not os.path.isfile(usrDirVerif):
                        currentUsrFile = open(usrDirVerif, 'w')
                        # Escribe la linea, luego cierra el archivo
                        currentUsrFile.write(emisorName + ': ' + emisorDesc)
                        currentUsrFile.write('\n')
                        usrHandlers[emisorName] = ''
                        currentUsrFile.close()  # Cierra el archivo tras la escritura
                    else:
                        # Comprueba la existencia del ID
                        if not emisorName in usrHandlers:  # NOTA, MIGRAR A JSON PORQUE NO PODEMOS HACER LA DETECCIÓN DE EXISTENCIA DE OTRA MANERA
                            # Abre archivo para edición
                            currentUsrFile = open(usrDirVerif, 'a')

                            # Escribe la linea, luego cierra el archivo
                            currentUsrFile.write(emisorName + ': ' + emisorDesc)
                            currentUsrFile.write('\n')
                            usrHandlers[emisorName] = ''
                            currentUsrFile.close()  # Cierra el archivo tras la escritura
            
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
