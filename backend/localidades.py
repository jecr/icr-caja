# -*- coding: UTF-8 -*-
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
