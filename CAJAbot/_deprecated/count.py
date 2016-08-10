# -*- coding: UTF-8 -*-
import json
import sys

inputFile = sys.argv[1]  # Archivo a contar

archivoAbierto = open(inputFile, 'r')

contenedorTuits = []

for linea in archivoAbierto:
	contenedorTuits.append(linea)

print len(contenedorTuits)

rts = 0
rpl = 0
mnc = 0

for linea in contenedorTuits:
	containerJson = json.loads(linea)
	if containerJson['text'].find('RT @') == 0:
		rts += 1

for linea in contenedorTuits:
	containerJson = json.loads(linea)
	if containerJson['in_reply_to_status_id_str'] != None:
		rpl += 1

for linea in contenedorTuits:
	containerJson = json.loads(linea)
	if containerJson['in_reply_to_status_id_str'] == None and containerJson['text'].find('RT @') == -1:
		mnc += 1

print 'Publicaciones totales: ' + str(len(contenedorTuits))
print 'Retweets: ' + str(rts) + ', Replies: ' + str(rpl) + ', Mentions: ' + str(mnc)
