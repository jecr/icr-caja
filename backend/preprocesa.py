# -*- coding: UTF-8 -*-
# =========================================================================
# = Preprocesado de enlaces, devuelve el contenido del archivo *_vis.json =
# =========================================================================


def getInD(item):  # Mini-función para el ordenado de elementos
    return item['inDegree']


def preprocesa(workingLinks, listadoDeHandlers):

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
        if item in listadoDeHandlers:
            nodo['class'] = listadoDeHandlers[item]
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
