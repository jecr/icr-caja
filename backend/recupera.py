# -*- coding: UTF-8 -*-
import json
from nltk.stem import SnowballStemmer
import os
import pickle
import re
import sys
from textblob.classifiers import NaiveBayesClassifier
import time
import tweepy
import webbrowser

# =======================================
# ====== CLASIFICACIÓN DE USUARIOS ======
# =======================================


def getInD(item):  # Mini-función para el ordenado de elementos
    return item['inDegree']


def preprocesa(workingLinks):

    preNodes = []

    for item in workingLinks:
        preNodes.append(item['source'])
        preNodes.append(item['target'])

    preNodes = list(set(preNodes))

    nodes = []
    for item in preNodes:
        nodo = {}
        nodo['index'] = preNodes.index(item)
        nodo['name'] = item
        if item in handlersAlmacenados:
            nodo['class'] = handlersAlmacenados[item]
        else:
            nodo['class'] = 'Error'
        nodes.append(nodo)

    for item in nodes:
        item['inDegree'] = 0
        for subitem in workingLinks:
            if item['name'] == subitem['target']:
                item['inDegree'] += 1

    nodes.sort(key=getInD, reverse=True)

    topNodes = []
    rangeMax = 0
    if len(nodes) < 30:
        rangeMax = len(nodes)
    else:
        rangeMax = 30

    for x in xrange(0, rangeMax):
        topNodes.append(nodes[x])

    for item in nodes:
        if item['inDegree'] > 15 and item['class'] == 'politico':
            topNodes.append(item)
        if item['inDegree'] > 50 and item['class'] == 'medio':
            topNodes.append(item)

    linkedByIndex = {}
    for item in workingLinks:
        linkedByIndex[item['source'] + ',' + item['target']] = ''

    adjacencyListTotal = {}  # {nombre = [a, b, c]}
    for item in nodes:
        neighborhood = []
        for subitem in nodes:
            if item['name'] + ',' + subitem['name'] in linkedByIndex or subitem['name'] + ',' + item['name'] in linkedByIndex and item['name'] != subitem['name']:
                neighborhood.append(subitem['name'])
        adjacencyListTotal[item['name']] = neighborhood

    preNodeSample = []
    nodeSample = []
    for item in topNodes:
        preNodeSample.append(item['name'])
        for subitem in adjacencyListTotal[item['name']]:
            preNodeSample.append(subitem)

    preNodeSample = list(set(preNodeSample))

    for item in nodes:
        for subitem in preNodeSample:
            if item['name'] == subitem:
                nodeSample.append(item)

    adjacencyList = {}
    for item in nodeSample:
        neighborhood = []
        for subitem in nodeSample:
            if item['name'] + ',' + subitem['name'] in linkedByIndex or subitem['name'] + ',' + item['name'] in linkedByIndex and item['name'] != subitem['name']:
                neighborhood.append(subitem['name'])
        adjacencyList[item['name']] = neighborhood

    totalInteractions = []
    for item in adjacencyList:
        for subitem in adjacencyList[item]:
            for subsubitem in workingLinks:
                if subsubitem['source'] == item and subsubitem['target'] == subitem:
                    totalInteractions.append(subsubitem)

    salidaArchivo = {}
    salidaArchivo['nodes'] = nodes
    salidaArchivo['links'] = workingLinks
    salidaArchivo['node_sample'] = nodeSample
    salidaArchivo['total_interactions'] = totalInteractions

    return salidaArchivo

# =======================================
# ====== CLASIFICACIÓN DE USUARIOS ======
# =======================================

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

# ===========================================
# ====== RECUPERACIÓN DE DESCRIPCIONES ======
# ===========================================


def recuperaUsuario(nombUsuario):
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

# ====================================================
# ====== SIMILITUD DE CADENAS, PARA LOCALIDADES ======
# ====================================================

archivoLugares = open('util/locationsmx.txt', 'r')
lugaresMx = {}
for item in archivoLugares:
    lugaresMx[item.strip()] = ''


def locSimilarity(thisLocation):
    locSim = {}
    locSim['score'] = 0

    if thisLocation in lugaresMx:
        return 1
    else:
        for item in lugaresMx:
            cadena = thisLocation
            comp = item
            coincide = ''
            minimo_coinc = 90

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
                        end += 1

                        if len(coincide) < len(needle):
                            coincide = needle

                        desfase = 0
                        needle = ''
                        for item in range(start, start + end):
                            if (desfase + start) < len(cadena):
                                needle += list(cadena)[desfase + start]
                            else:
                                needle = 'null'
                            desfase += 1

                    start += 1
                    if start < len(cadena):
                        needle = list(cadena)[start]
                similarity['score'] = ((len(coincide) * 100) / len(cadena))

            # if  similarity['score'] > minimo_coinc and similarity['score'] > locSim['score'] and abs(((len(cadena) - len(comp)) * 100) / len(comp)) < 20:
            if similarity['score'] > minimo_coinc and similarity['score'] > locSim['score']:
                locSim['score'] = similarity['score']

        if locSim['score'] != 0:
            return 1
        else:
            return 0

# ===========================================
# ====== RECUPERADOR DE CONVERSACIONES ======
# ===========================================

# Recuperación de conversación sobre este tweet: REQUIERE DE MEJORAS, COMPLEMENTAR EN ACTUALIZACIÓN POSTERIOR
# if getConversation(toUser, toUserStId, api) == 'newKeyNeeded':
#     claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
#     api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave


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

usrHandlers = {}
currentUsrFile = ''

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

while (time.time() - execStart) < (60 * 1):
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
                        if locSimilarity(emisor['location']) != 0:
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
                    toUser = jsondTweet['user']['screen_name'].lower()
                    toUserStId = jsondTweet['id']

                    # Separa la fecha del archivo, la convierte en fecha por día
                    currentDate = str(jsondTweet['created_at']).split(' ')[1] + '-' + str(
                        jsondTweet['created_at']).split(' ')[2] + '-' + str(jsondTweet['created_at']).split(' ')[5]

                    # (ENTRADA) Si el archivo no existe, lo crea
                    dirVerif = projectTweets + '/' + projectTweets + '_' + currentDate + '(file_not_used).txt'
                    # NUEVOS ARCHIVOS (EN JSON)
                    archivoTweets = projectTweets + '/' + projectTweets + '_' + currentDate + '.json'
                    archivoViz = projectTweets + '/' + projectTweets + '_network_vis.json'

                    # RE-ARRANGEMENT OF METADATA
                    # Metadatos para cada tweet
                    meta_tweet = {}
                    meta_screen_name = jsondTweet['user']['screen_name'].lower().encode('UTF-8').replace('\n', '').replace('\r', '')
                    meta_screen_name = ' '.join(meta_screen_name.split())
                    
                    meta_description = jsondTweet['user']['description'].encode('UTF-8')
                    meta_description = meta_description.replace('\n', '').replace('\r', '')
                    meta_description = ' '.join(meta_description.split())

                    meta_location = jsondTweet['user']['location'].encode('UTF-8').replace('\n', '').replace('\r', '')
                    meta_location = ' '.join(meta_location.split())

                    if tweetStatus['rt'] == 1:
                        meta_tweet['int_type'] = 'retweet'
                    if tweetStatus['rp'] == 1:
                        meta_tweet['int_type'] = 'reply'
                    if tweetStatus['mn'] == 1:
                        meta_tweet['int_type'] = 'mention'

                    meta_tweet['screen_name'] = meta_screen_name

                    meta_tweet['id'] = jsondTweet['id']

                    if jsondTweet['in_reply_to_screen_name'] is not None:
                        meta_in_reply_to_screen_name = jsondTweet['in_reply_to_screen_name'].lower(
                        ).encode('UTF-8').replace('\n', '').replace('\r', '')
                        meta_in_reply_to_screen_name = ' '.join(
                            meta_in_reply_to_screen_name.split())
                        meta_tweet['in_reply_to_screen_name'] = meta_in_reply_to_screen_name
                    else:
                        meta_tweet['in_reply_to_screen_name'] = 'empty'

                    if jsondTweet['in_reply_to_status_id'] is not None:
                        meta_in_reply_to_status_id = jsondTweet['in_reply_to_status_id']
                        meta_tweet['in_reply_to_status_id'] = meta_in_reply_to_status_id
                    else:
                        meta_tweet['in_reply_to_status_id'] = 'empty'

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
                    emisor_meta['class'] = clasifica(emisor_meta)
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
                        destina_meta['class'] = clasifica(destina_meta)
                    # REPLY
                    if meta_tweet['int_type'] == 'reply':
                        destina_meta['handler'] = jsondTweet['in_reply_to_screen_name'].lower().encode(
                            'UTF-8').replace('\n', '').replace('\r', '')
                        userMeta = recuperaUsuario(destina_meta['handler'])
                        destina_meta['description'] = userMeta['description']
                        destina_meta['location'] = userMeta['location']
                        destina_meta['class'] = clasifica(destina_meta)
                    # MENTION
                    if meta_tweet['int_type'] == 'mention':
                        for item in jsondTweet['entities']['user_mentions']:
                            destina_meta['handler'] = item['screen_name'].lower().encode(
                                'UTF-8').replace('\n', '').replace('\r', '')
                            userMeta = recuperaUsuario(destina_meta['handler'])
                            destina_meta['description'] = userMeta['description']
                            destina_meta['location'] = userMeta['location']
                            destina_meta['class'] = clasifica(destina_meta)

                    # Agrega a la lista de usuarios de este tweet los implicados (sólo es posible un tipo de interacción por tweet)
                    handlersList.append(destina_meta)
                    # ENDS REARRANGEMENT

                    if os.path.isfile(archivoTweets):
                        if execStatus['continue'] == 0:
                            print("El archivo " + archivoTweets + " ya existe")
                            print("Continue flag set to: " + str(execStatus['continue']))
                            fOpen = open(archivoTweets, 'r')
                            loaded_tweets_file = json.load(fOpen)
                            
                            # Recorre y almacena tweets en dict
                            print("Recuperando datos de archivo preexistente...")
                            count_users = 0
                            for item in loaded_tweets_file['tweets']:
                                idsAlmacenadas[item['id']] = ''
                                item['text'] = item['text'].encode('UTF-8')
                                tweets_to_save.append(item)

                                # Genera metadatos de enlace
                                enlaceActual = {}
                                enlaceActual['source'] = item['screen_name']
                                # RETWEET
                                if meta_tweet['int_type'] == 'retweet':
                                    item_handler = jsondTweet['retweeted_status']['user']['screen_name'].lower().encode('UTF-8').replace('\n', '').replace('\r', '')
                                # REPLY
                                if meta_tweet['int_type'] == 'reply':
                                    item_handler = jsondTweet['in_reply_to_screen_name'].lower().encode('UTF-8').replace('\n', '').replace('\r', '')
                                # MENTION
                                if meta_tweet['int_type'] == 'mention':
                                    for item in jsondTweet['entities']['user_mentions']:
                                        item_handler = item['screen_name'].lower().encode('UTF-8').replace('\n', '').replace('\r', '')
                                enlaceActual['target'] = item_handler
                                enlaceActual['interaction'] = item['int_type']
                                enlaceActual['retuits'] = 1

                                # Añade la interacción a la lista de enlaces
                                links_to_preprocess.append(enlaceActual)

                            # Recorre y almacena handlers en dict
                            for item in loaded_tweets_file['users']:
                                handlersAlmacenados[item['handler'].encode('UTF-8')] = item['class']
                                item['description'] = item['description'].encode('UTF-8')
                                item['location'] = item['location'].encode('UTF-8')
                                usrsAlmacenar.append(item)
                                count_users = count_users + 1
                            
                            print(str(len(links_to_preprocess)) + " interacciones recuperadas de archivos existentes.")
                            print("Usuarios pre-existentes:" + str(count_users))
                            execStatus['continue'] = 1
                            print("Continue flag set to: " + str(execStatus['continue']))
                    else:
                        execStatus['continue'] = 0
                        print("Continue flag set to: " + str(execStatus['continue']))
                        print("New file: " + dirVerif)

                    # Verificación de pre-existencia (TWT)
                    if not meta_tweet['id'] in idsAlmacenadas:
                        tweets_to_save.append(meta_tweet)
                        idsAlmacenadas[meta_tweet['id']] = ''
                        
                        # Genera el arreglo a exportar
                        continuable_file['tweets'] = tweets_to_save

                        # Genera metadatos de enlace
                        enlaceActual = {}
                        enlaceActual['source'] = emisor_meta['handler']
                        enlaceActual['target'] = destina_meta['handler']
                        enlaceActual['interaction'] = meta_tweet['int_type']
                        enlaceActual['retuits'] = 1
                            
                        # Añade la interacción a la lista de enlaces
                        links_to_preprocess.append(enlaceActual)
                        for item in handlersList:

                            # Verificación de pre-existencia (USR)
                            if not item['handler'] in handlersAlmacenados:
                                usrsAlmacenar.append(item)
                                handlersAlmacenados[item['handler']] = item['class']
                                
                                # Genera el arreglo a exportar
                                continuable_file['users'] = usrsAlmacenar
                        with open(archivoTweets, 'w') as f:
                            json.dump(continuable_file, f, indent=4, ensure_ascii=False)
                        
                        print("Tamaño de archivo de visualización: " + str(len(links_to_preprocess)))
                        # Archivo para visualización:
                        with open(archivoViz, 'w') as f:
                            json.dump(preprocesa(links_to_preprocess), f, indent=4, ensure_ascii=False)

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
                claveActualIndex = keySwitch(claveActualIndex)
                # Conexión usando nueva clave
                api = tweepy.API(conexion(claveActualIndex))
                break
    except Exception, e:
        if hasattr(e, 'response'):
            if hasattr(e.response, 'status_code'):
                if e.response.status_code == 429:
                    # Genera un nuevo índice de clave
                    claveActualIndex = keySwitch(claveActualIndex)
                    # Conexión usando nueva clave
                    api = tweepy.API(conexion(claveActualIndex))
            else:
                print e.response
                pass
        else:
            print e
            pass
