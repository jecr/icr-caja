# -*- coding: UTF-8 -*-
import json
import sys

# Arg1 = Lista de publicaciones
# Arg2 = Usuarios Clasificados

f = sys.argv[1]
fOpen = open(f, 'r')
publics = json.load(fOpen)

fa = sys.argv[2]
fOpenA = open(fa, 'r')
clasfdUsr = json.load(fOpenA)

clasificados = {}
for item in clasfdUsr:
    clasificados[item['name']] = item['category'].encode('UTF-8')

links = []

retuits = 0
menciones = 0
respuestas = 0

for item in publics:
    actual = {}
    # RETWEETS
    if item['text'].find('RT @') == 0:
        origenRt = item['from_user'].lower().encode('UTF-8')
        actual['source'] = origenRt
        spltTwt = item['text'].lower().encode('UTF-8')
        spltTwt = spltTwt.split()
        usrRtw = spltTwt[1].replace('@', '').replace(':', '')
        if origenRt != usrRtw:
            actual['target'] = usrRtw
            actual['interaction'] = 'retweet'
            actual['retuits'] = 1
            if actual != {}:
                links.append(actual)
                retuits += 1

    # REPLIES
    if item['in_reply_to_status_id_str'] != 'None' and item['in_reply_to_screen_name'] != item['from_user']:
        actual['source'] = item['from_user'].lower().encode('UTF-8')
        actual['target'] = item['in_reply_to_screen_name'].lower().encode('UTF-8')
        actual['interaction'] = 'reply'
        actual['replies'] = 1
        if actual != {}:
            links.append(actual)
            respuestas += 1
        for mencion in item['user_mentions']:
            subActual = {}
            subActual['source'] = actual['source']
            subActual['target'] = mencion.lower().encode('UTF-8')
            subActual['interaction'] = 'reply'
            subActual['replies'] = 1
            if subActual['source'] != subActual['target'] and actual['target'] != subActual['target']:
                if subActual != {}:
                    links.append(subActual)
                    menciones += 1

    # MENTIONS
    if item['in_reply_to_status_id_str'] == 'None' and item['text'].find('RT @') == -1 and len(item['user_mentions']) > 0:
        for mencion in item['user_mentions']:
            if mencion != item['from_user']:
                actual = {}
                actual['source'] = item['from_user'].lower().encode('UTF-8')
                actual['target'] = mencion.lower().encode('UTF-8')
                actual['interaction'] = 'mention'
                actual['mentions'] = 1
                if actual != {}:
                    links.append(actual)
                    menciones += 1

preNodes = []

for item in links:
    preNodes.append(item['source'])
    preNodes.append(item['target'])

preNodes = list(set(preNodes))

nodes = []
for item in preNodes:
    nodo = {}
    nodo['index'] = preNodes.index(item)
    nodo['name'] = item
    if item in clasificados:
        nodo['class'] = clasificados[item]
    else:
        nodo['class'] = 'Error'
    nodes.append(nodo)

for item in nodes:
    item['inDegree'] = 0
    for subitem in links:
        if item['name'] == subitem['target']:
            item['inDegree'] += 1


def getInD(item):
    return item['inDegree']

nodes.sort(key=getInD, reverse=True)

topNodes = []
for x in xrange(0, 30):
    topNodes.append(nodes[x])

for item in nodes:
    if item['inDegree'] > 15 and item['class'] == 'politico':
        topNodes.append(item)
    if item['inDegree'] > 50 and item['class'] == 'medio':
        topNodes.append(item)

linkedByIndex = {}
for item in links:
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
        for subsubitem in links:
            if subsubitem['source'] == item and subsubitem['target'] == subitem:
                totalInteractions.append(subsubitem)

salidaArchivo = {}
salidaArchivo['nodes'] = nodes
salidaArchivo['links'] = links
salidaArchivo['node_sample'] = nodeSample
salidaArchivo['total_interactions'] = totalInteractions

# Escritura del archivo al terminar la ejecución
archivoRuta = sys.argv[1].replace('.json', '_preprocesado.json')
with open(archivoRuta, 'w') as f:
    json.dump(salidaArchivo, f, indent=4, ensure_ascii=False)
