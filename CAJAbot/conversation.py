# -*- coding: UTF-8 -*-
import json
import os
import sys
import tweepy


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

f = sys.argv[1]
tuitsFile = open(f, 'r')

# Ruta del archivo a escribir
fConvs = sys.argv[1].split('.')
fConvs = fConvs[0] + '-conversations.txt'
if os.path.isfile(fConvs):
    convsFile = open(fConvs, 'r')
    for item in convsFile:
        item = json.loads(item)
        idsTotales[item['id']] = ''
    convsFile.close()
    convsFile = open(fConvs, 'a')
else:
    convsFile = open(fConvs, 'w')

tuits = {}
idsTotales = {}
for item in tuitsFile:
    item = json.loads(item)
    tuits[item['user']['screen_name'].encode('UTF-8')] = item['id']
    idsTotales[item['id']] = ''

for entrada in tuits:
    search_query = 'to:' + entrada
    try:
        for page in tweepy.Cursor(api.search, q=search_query, since_id=tuits[entrada], lang="es", include_entities=True, count=100).pages(10):
            for tweet in page:
                prinTweet = json.dumps(tweet._json)
                tweet = json.loads(prinTweet)
                if tweet['in_reply_to_status_id'] == tuits[entrada] and not tweet['id'] in idsTotales:
                    # print 'Recuperando para ' + str(tuits[entrada]) + ' de ' + entrada
                    # print tweet['user']['screen_name'].encode('UTF-8') + ': ' + tweet['text'].encode('UTF-8')
                    convsFile.write(prinTweet)
                    convsFile.write('\n')
                    idsTotales[tweet['id']] = ''

                    # ONE LEVEL DOWN (The tweetception starts)
                    # Consigue el id del tweet actual, luego recupera el nombre de usuario
                    UNO_idUsuario = tweet['user']['screen_name'].lower()
                    UNO_tuitId = tweet['id']
                    UNO_subQuery = 'to:' + UNO_idUsuario
                    for UNO_subPage in tweepy.Cursor(api.search, q=UNO_subQuery, since_id=UNO_tuitId, lang="es", include_entities=True, count=100).pages(10):
                        for UNO_subTweet in UNO_subPage:
                            UNO_printSubTweet = json.dumps(UNO_subTweet._json)
                            UNO_subTweet = json.loads(UNO_printSubTweet)
                            if UNO_subTweet['in_reply_to_status_id'] == UNO_tuitId and not tweet['id'] in idsTotales:
                                convsFile.write(UNO_printSubTweet)
                                convsFile.write('\n')
                                # print '\t\t' + UNO_subTweet['user']['screen_name'].encode('UTF-8') + ': ' + UNO_subTweet['text'].encode('UTF-8')

    except Exception, e:
        if hasattr(e, 'response'):
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 429:
                    print '\nExcepción: Límite de solicitudes alcanzado'
                    claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
                    api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave
            else:
                print e.response
                pass
        else:
            print e
            print 'Exception attributes error'
            pass 
