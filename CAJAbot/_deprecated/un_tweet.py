# -*- coding: UTF-8 -*-
import json
import sys
import tweepy
import time
import webbrowser

consumer_key = 'ZR2SU5TrGKQ2zCbVbyDUw'
consumer_secret = 'Rcg5Esw9z6z8JdIEfJIp4NBRzgxA3i6ISeCL1mDM'

access_token = '108874877-5N9XRZiRCTiALdKUw7sYhulzNgwFUzZgfeOw03b9'
access_token_secret = 'ogKVKjkRUie0cfP95zcT2kINVeZrbm1iyxj90dCpVwjFG'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

esteTuit = sys.argv[1]  # ID de tweet en cuestión

tweetData = api.get_status(esteTuit)
tweetData = json.dumps(tweetData._json)
parsedTweet = json.loads(tweetData)

webbrowser.open_new('https://twitter.com/' + parsedTweet['user']['screen_name'] + '/status/' + esteTuit)