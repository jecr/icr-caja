# -*- coding: UTF-8 -*-
# Recuperación de descripciones por nombre de usuario
# NOTA: Crear lista de usuarios no encontrados/con descripciones vacías
import json
import os
import sys
import tweepy

print '===== INICIO DE EJECUCIÓN ====='


def recuperaDescripcion(nombUsuario):
    user = api.get_user(nombUsuario)
    treatedText = user.description
    treatedText = treatedText.replace('\n', '')
    treatedText = treatedText.replace('\r', '')
    treatedText = ' '.join(treatedText.split())  # Separación - unión para remover espacios de más
    return treatedText


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

# Lista de usuarios a recuperar
archivo1 = sys.argv[1]
lista = open(archivo1)

# Lista de nombres de usuario a recuperar
aRecuperar = []
for username in lista:
    aRecuperar.append(username.strip())

# Diccionario con nombres de usuario = descripción
yaRecuperados = {}

# Archivo de salida
# Ajuste de nombre de archivo
nombreArchivo = archivo1.split('.')[0] + ('-recuperados.json')
if os.path.isfile(nombreArchivo):  # Si el archivo existe, es abierto para lectura
    outputFile = open(nombreArchivo, 'r')
    archivoDescripciones = json.load(outputFile)  # Carga el archivo JSON
    print 'Archivo cargado: ' + str(len(archivoDescripciones))
    for linea in archivoDescripciones:  # Crea el diccionario de usuarios ya recuperados
        yaRecuperados[linea['name']] = linea['description']
    outputFile.close()
else:
    print 'Archivo de descripciones no encontrado, inicializando...'

# Información pertinente
print '\n' + str(len(yaRecuperados)) + '/' + str(len(aRecuperar)) + ' usuarios recuperados\n'

# Ciclo principal
for usuario in aRecuperar:
    if not usuario in yaRecuperados:  # Si el usuario no ha sido aún recuperado
        try:
            if consultasRestantes() < 1:
                print '\nLímite de solicitudes alcanzado'
                print str(len(yaRecuperados)) + '/' + str(len(aRecuperar)) + ' usuarios recuperados'
                claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
                api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave
            # Fin de consulta
            print '\nRecuperando: ' + usuario + '...'
            try:
                descripcion = recuperaDescripcion(usuario)
                if descripcion != '' and descripcion != ' ':  # Si la decripción no está vacía, es guardada
                    yaRecuperados[usuario] = json.loads(json.dumps(descripcion))
                    print 'Descripción recuperada'
                else:
                    print 'Descripción vacía'
            except Exception, e:
                print 'Usuario no encontrado'
        except Exception, e:
            if hasattr(e, 'response'):
                if hasattr(e.response, 'status_code'):
                    if e.response.status_code == 429:
                        print '\nExcepción: Límite de solicitudes alcanzado'
                        print str(len(yaRecuperados)) + '/' + str(len(aRecuperar)) + ' usuarios recuperados'
                        claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
                        api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave
                        print '\nRecuperando: ' + usuario + '...\r'
                        try:
                            descripcion = recuperaDescripcion(usuario)
                            if descripcion != '' and descripcion != ' ':  # Si la decripción no está vacía, es guardada
                                yaRecuperados[usuario] = json.loads(json.dumps(descripcion))
                                print 'Descripción recuperada'
                            else:
                                print 'Descripción vacía'
                        except Exception, e:
                            print 'Usuario no encontrado'
                else:
                    usuario = usuario.replace('\n', '').replace('\r', '')
                    yaRecuperados[usuario] = 'error'
                    print usuario
                    print 'User recovery error'
                    print e.response
                    pass
            else:
                print 'Exception attributes error'
                pass

toPrintFile = []  # Lista de diccionarios con valores name y description
for elemento in yaRecuperados:
    motil = {}
    laDescripcion = yaRecuperados[elemento]
    try:
        laDescripcion = laDescripcion.encode('UTF-8')
        usuario = usuario.replace('\n', '').replace('\r', '')
    except Exception, e:
        print 'Encoding exception'
    motil['name'] = elemento
    motil['description'] = laDescripcion
    toPrintFile.append(motil)

# Escritura del archivo al terminar la ejecución
with open(nombreArchivo, 'w') as f:
    json.dump(toPrintFile, f, indent=4, ensure_ascii=False)

print '\nArchivo final ' + nombreArchivo + ' guardado. Have a nice day :)\n'
