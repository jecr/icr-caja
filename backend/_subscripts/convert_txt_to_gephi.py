# -*- coding: UTF-8 -*-
import json
import sys

inputFile = sys.argv[1]  # Archivo a convertir

archivoAbierto = open(inputFile, 'r')

baseFileName = inputFile.replace('.txt', '')

# listaUsuarios = open(baseFileName + '-usuarios.csv', 'w')
# listaUsuarios.write('id,actor_type\n')

# Reglas:
# Es RETWEET si al inicio de la publicación hay un "RT @"
# Es respuesta si el campo in_reply_to_status_id_str
# Es mención pura si sobra después de esto

rts = 0
rpl = 0
mnc = 0

dictUsuarios = {}
temporalTuitsContainer = []
publics = 0


def extraMentions(elOtroTuit):
    for mencion in elOtroTuit['entities']['user_mentions']:
        cadena = elOtroTuit['user']['screen_name'].lower() + ',' + mencion['screen_name'].lower() + ',mention'
        temporalTuitsContainer.append(cadena)

# Recorrido de los datos
for linea in archivoAbierto:
    publics += 1
    tuit = json.loads(linea)

    # Si hay RT @, es retweet
    if tuit['text'].find('RT @') == 0:
        rts += 1
        cadena = tuit['user']['screen_name'].lower() + ',' + tuit['entities']['user_mentions'][0]['screen_name'].lower() + ',retweet'
        temporalTuitsContainer.append(cadena)
        # Aquí incluía a los usuarios mencionados en un tweet retuiteado, ya no, nunca, nevermore
        # createList(tuit)
        # del tuit['user_mentions'][0]
        # extraMentions(tuit)

    # Si hay reply, es reply
    if tuit['in_reply_to_status_id_str'] != None:
        rpl += 1
        cadena = tuit['user']['screen_name'].lower() + ',' + tuit['in_reply_to_screen_name'].lower() + ',reply'
        temporalTuitsContainer.append(cadena)
        extraMentions(tuit)

    # Si no hay reply && no hay RT @ && user mentions es mayor a 0, es mención
    if tuit['in_reply_to_status_id_str'] == None and tuit['text'].find('RT @') == -1 and len(tuit['entities']['user_mentions']) > 0:
        mnc += 1
        for mencion in tuit['entities']['user_mentions']:
            cadena = tuit['user']['screen_name'].lower() + ',' + mencion['screen_name'].lower() + ',mention'
            temporalTuitsContainer.append(cadena)

# Elimino self-loops
selfies = 0
archivoGephi = open(baseFileName + '-gephi.csv', 'w+')
archivoGephi.write('source,target,int_type\n')

for interaccion in temporalTuitsContainer:
    parte = interaccion.split(',')
    if parte[0] == parte[1]:
        selfies += 1
    else:
        dictUsuarios[parte[0]] = ''
        dictUsuarios[parte[1]] = ''
        archivoGephi.write(interaccion + '\n')

# Convierte el nombre de archivo de tweets para
# crear el archivo de usuarios clasificados correspondiente
# usuariosFileRoute = baseFileName.replace('filtro', 'clasif')
# usuariosFileRoute += '_clas.json'

# Abre el archivo para lectura y lo jsonparsea asignándolo a una variable
# archivoUsuarios = open(usuariosFileRoute, 'r')
# dictJsonUsuarios = {}
# contenedorJsonUsuarios = json.load(archivoUsuarios)
# for entrada in contenedorJsonUsuarios:
#     dictJsonUsuarios[entrada['name']] = entrada['score']

# Impresión de usuarios y su tipo
# Por cada nombre de usuario, comprueba su existencia en el arreglo de usuarios
# De existir, asigna el tipo de usuario, de otra manera, asigna 'undefined'
# Finalmente, escribe estos datos en un archivo
# for username in dictUsuarios:
#     if username in dictJsonUsuarios:
#         actorType = ',' + str(dictJsonUsuarios[username])
#     else:
#         actorType = ',undefined'
#     listaUsuarios.write(username + actorType + '\n')

# Conteo estadístico de publicaciones y usuarios, así como sus tipos
print '\nPublicaciones totales: ' + str(publics)
print 'Retweets: ' + str(rts) + ', Replies: ' + str(rpl) + ', Mentions: ' + str(mnc) + '\nUsuarios: ' + str(len(dictUsuarios)) + ' ::: Self-loops: ' + str(selfies) + '\n'
