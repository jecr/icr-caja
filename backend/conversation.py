# -*- coding: UTF-8 -*-
# ===========================================
# ====== RECUPERADOR DE CONVERSACIONES ======
# ===========================================

import json
import tweepy

# Recuperación de conversación sobre este tweet: REQUIERE DE MEJORAS, COMPLEMENTAR EN ACTUALIZACIÓN POSTERIOR
# if getConversation(toUser, toUserStId, api) == 'newKeyNeeded':
#     claveActualIndex = keySwitch(claveActualIndex)  # Genera un nuevo índice de clave
#     api = tweepy.API(conexion(claveActualIndex))  # Conexión usando nueva clave


def getConversation(theUser, theUserTweetId, theApi, currentTweetsFile, idsDictionary):
    cadenaBusqueda = 'to:' + theUser
    try:
        for page in tweepy.Cursor(theApi.search, q=cadenaBusqueda, since_id=theUserTweetId, lang="es", include_entities=True, count=100).pages(10):
            for convTweet in page:
                prinTweet = json.dumps(convTweet._json)
                convTweet = json.loads(prinTweet)
                if convTweet['in_reply_to_status_id'] == theUserTweetId and not convTweet['id'] in idsDictionary:
                    currentTweetsFile.write(prinTweet)
                    currentTweetsFile.write('\n')
                    idsDictionary[convTweet['id']] = ''

                    # ONE LEVEL DOWN (The tweetception starts)
                    # Consigue el id del tweet actual, luego recupera el nombre de usuario
                    UNO_idUsuario = convTweet['user']['screen_name'].lower()
                    UNO_tuitId = convTweet['id']
                    UNO_subQuery = 'to:' + UNO_idUsuario
                    for UNO_subPage in tweepy.Cursor(theApi.search, q=UNO_subQuery, since_id=UNO_tuitId, lang="es", include_entities=True, count=100).pages(10):
                        for UNO_subTweet in UNO_subPage:
                            UNO_printSubTweet = json.dumps(UNO_subTweet._json)
                            UNO_subTweet = json.loads(UNO_printSubTweet)
                            if UNO_subTweet['in_reply_to_status_id'] == UNO_tuitId and not convTweet['id'] in idsDictionary:
                                currentTweetsFile.write(UNO_printSubTweet)
                                currentTweetsFile.write('\n')
                                idsDictionary[convTweet['id']] = ''

    except Exception, e:
        print e
        pass
