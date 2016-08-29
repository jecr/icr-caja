# -*- coding: UTF-8 -*-
import json
import os
import sys
import time
import tweepy

# Diccionario con claves de aplicaciones, es posible elegir una para hacer la recuperación
twitter_keys = {}

twitter_keys['alfa'] = {}
twitter_keys['alfa']['c_k'] = '6oJLTuH6Hb5bhoflAkh2EQZTf'
twitter_keys['alfa']['c_s'] = 'kQh9v4OM4plxLbpBCjkYk54iCTA3F23deJkzDXXCZvIlsmAQKN'
twitter_keys['alfa']['a_t'] = '108874877-vQqPqkK9afIZYZi89VkHqhvO0UKKO7gafKVi7pMS'
twitter_keys['alfa']['a_ts'] = 'wkpEye49yW3LuMmBGV82IsasHqprjSU2FMWc59SYe4bJJ'

twitter_keys['bravo'] = {}
twitter_keys['bravo']['c_k'] = 'X9mFEYo8smhDkSVQRPdkLDPis'
twitter_keys['bravo']['c_s'] = 'KwUWaBKxm5nslS1xBpByn5w1leYPoR5tAfuVV4JnCCPsyK077F'
twitter_keys['bravo']['a_t'] = '108874877-FqRfNGmRlsAoOX13umHyCUnLTb8BT9Fn97aL1awa'
twitter_keys['bravo']['a_ts'] = 'biUkbDcfpD5mJ2r9Cbw1V6UAh9QXipzja2am3OTEGAmWb'

twitter_keys['charlie'] = {}
twitter_keys['charlie']['c_k'] = 'QxEiwkObtSNCM2PVIdeUktCCf'
twitter_keys['charlie']['c_s'] = 'Jgb87eswqGChTISs8ISOfy6hvg77PPeF7fT3sCAy14bN03xLvx'
twitter_keys['charlie']['a_t'] = '108874877-M81jUTUDZXj6Cj86iAELibQHFCo7aZYstKucC5fY'
twitter_keys['charlie']['a_ts'] = 'OfeBrxSNvBaBr7qyUcfLPtvJopxk2pZk1S99MFla0mGdu'

# python recover.py alfa "\"hoy no circula\" OR hoynocircula OR contingenciaambiental OR \"contingencia ambiental\" OR precontingencia" hoy_no_circula
# python recover.py alfa "\"hacienda blanca\" OR haciendablanca OR oaxacagrita OR nochixtlan OR oaxaca OR cnte" oaxaca
# python recover.py bravo "panamapapers OR \"papeles de panama\"" panama_papers
# python recover.py charlie debateoaxaca2016 debate_oaxaca

# Selección de aplicación para recuperación
app_selection = sys.argv[1]  # Claves de aplicación
search_query = sys.argv[2]  # Término(s) de búsqueda
projectTweets = sys.argv[3]  # Nombre del proyecto

consumer_key = twitter_keys[app_selection]['c_k']
consumer_secret = twitter_keys[app_selection]['c_s']

access_token = twitter_keys[app_selection]['a_t']
access_token_secret = twitter_keys[app_selection]['a_ts']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Comprueba la existencia del directorio
if not os.path.exists(projectTweets):
    print '\n' + projectTweets + ' no existe, creando...'
    os.makedirs(projectTweets)
    print '\n' + projectTweets + ' creado'
else:
    print "\nEl directorio ya existe"

if not os.path.isfile(projectTweets + '/query.txt'):
    terminos = open(projectTweets + '/query.txt', 'w')
    search_query = search_query.replace('"', '\\"')
    terminos.write(search_query)
    print 'Archivo de cadena de búsqueda creado.'
else:
    print 'Archivo de cadena de búsqueda existente.'

savedDate = ''

# Inicializa el diccionario de IDs
dictIds = {}
nuevosTweets = 0
currentFile = ''

# 20 = 744955439058558976
# 19 = 744542604394536960
# Mon Jun 20 17:53:01 = 744951202287280129
# 19 midnight = 744757497152475136
# 20 10pm = 745104164720513026
# 21 10pm = 745466570734899205
# 22 11:55pm = 745857691650764800

# 23 11:55 = 746220071387693057
# 24 11:55 = 746582466954158084
# 25 11:30 = 746938601401880576
# 26 11:30 = 747301036352692225
# 27 11:50 = 747668376223363072
# 28 11:30 = 748025794354618368
# 29 10:01 = 748365694836809729
# 30 10:00 = 748728057922359296
# 1 11:56 = 749119436158672896
# 2 11:56 = 749481824993226752
# 3 11:56 = 749844209591390209 DONE

while 1 > 0:
    try:
        for page in tweepy.Cursor(api.search, q=search_query, max_id=749844209591390209, lang="es", count=100, include_entities=True).pages(100):
            # Procesamiento de tweets
            for tweet in page:
                cleanTweet = json.dumps(tweet._json)
                jsondTweet = json.loads(cleanTweet)  # Tweet parseado

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
                    nuevosTweets += 1  # Conteo de nuevos tweets por página
                    print 'File closed.'
                    currentFile.close()
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
                        nuevosTweets += 1  # Conteo de nuevos tweets por página
                        currentFile.close()  # Cierra el archivo tras la escritura

            # Consulta el límite restante de consultas
            data = api.rate_limit_status()
            remaining = data['resources']['search']['/search/tweets']['remaining']

            print str(remaining) + ' consultas restantes para ' + projectTweets + '   ',"           \r",
            # print str(remaining) + ' consultas restantes para ' + projectTweets

            # Fin consulta de límite
            if remaining < 1:
                print '\n' + str(nuevosTweets) + ' nuevas entradas.' # Imprime el número total de nuevas entradas, luego resetea la cuenta
                nuevosTweets = 0
                print app_selection + ' durmiendo zZzZzZ ' + time.asctime()
                time.sleep(60)
                break
    except Exception, e:
        if hasattr(e, 'response'):
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 429:
                    print 'Exception: ' + app_selection + ' durmiendo zZzZzZ ' + time.asctime()
                    time.sleep(60)
            else:
                print e.response
                pass
        else:
            print e
            pass
