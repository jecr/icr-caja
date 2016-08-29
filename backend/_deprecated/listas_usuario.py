# -*- coding: UTF-8 -*-
# Esta cosa imprime las listas creadas por jorgetuitea, fin
import json
import sys
import tweepy
import time

consumer_key = '6oJLTuH6Hb5bhoflAkh2EQZTf'
consumer_secret = 'kQh9v4OM4plxLbpBCjkYk54iCTA3F23deJkzDXXCZvIlsmAQKN'

access_token = '108874877-vQqPqkK9afIZYZi89VkHqhvO0UKKO7gafKVi7pMS'
access_token_secret = 'wkpEye49yW3LuMmBGV82IsasHqprjSU2FMWc59SYe4bJJ'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

listas = api.lists_all()

# x = 0
for lista in listas:
    # x += 1
    # if x > 1:
    #     break
    print '\n====== NUEVA LISTA:' + lista.name.upper() + '====='
    for page in tweepy.Cursor(api.list_members, 'jorgetuitea', lista.name, count=100).pages(100):
        for miembro in page:
            descripcion = miembro.description.encode('UTF-8')
            descripcion = descripcion.replace('\n', '')
            descripcion = descripcion.replace('\r', '')
            print miembro.screen_name.encode('UTF-8') + '==>"' + descripcion + '"'
