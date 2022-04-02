from itertools import count
from time import sleep
from tracemalloc import stop
from turtle import title
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib.request
import sys
import ast
from vkaudiotoken import get_vk_official_token

import vk_captchasolver as vc
import re
import vk_api
import vk_api
from vk_api.audio import VkAudio

#Your VK login and password

vkcreds = {
    "login":"79999999999",
    "password":"password"
}

#Getting VK Audio Token

vkaudiotoken = get_vk_official_token(vkcreds["login"], vkcreds["password"])
vkaudiotoken = vkaudiotoken["token"]

#Your spotify api client_id and client_secret

spotifycreds = {
    "client_id":"id",
    "client_secret":"secret"
}

#False to add from last added to first added tracks

reverse = False

#Id to your playlist
print('Insert Spotify playlist link')
match_spotify = re.search('([A-Z0-9])\w+', input())
playlist_id = match_spotify.group()

creds = SpotifyClientCredentials(client_id = spotifycreds["client_id"], client_secret=spotifycreds["client_secret"])
spotify = spotipy.Spotify(client_credentials_manager=creds)

results = spotify.user_playlist(user=None, playlist_id=f'{playlist_id}', fields="name")
data = spotify.playlist_tracks(playlist_id=f'{playlist_id}', limit=1, offset=0)

def getPlaylistName(results):
    return results['name']

def getArtists(data):
    artists = []
    for artist in data['items'][0]['track']['artists']:
        artists.append(artist['name'])
    if len(artists) == 1:
        return "".join(artists)
    return ", ".join(artists)

def getName(data):
    return data['items'][0]['track']['name']

def addtoPlaylist(list, data):
    artists = getArtists(data)
    name = getName(data)
    list.append(f'{artists} - {name}')

def captcha_handler(captcha):
    print('Trying to solve captcha...')
    imgURL = captcha.get_url()
    urllib.request.urlretrieve(imgURL, "captcha.png")
    key = vc.solve(image='captcha.png')
#   key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)

def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device

playlistName = getPlaylistName(results)

playlist = []

for i in range(data['total']):
    artists = getArtists(data)
    name = getName(data)
    data = spotify.playlist_tracks(playlist_id=f'{playlist_id}',limit=1, offset=i)
    playlist.append(f"{artists} - {name}")

#vk_session = vk_api.VkApi(vkcreds["login"], vkcreds["password"], vkaudiotoken, auth_handler=auth_handler,captcha_handler=captcha_handler)
vk_session = vk_api.VkApi(token=vkaudiotoken, captcha_handler=captcha_handler)
vk_session_audio = vk_api.VkApi(vkcreds["login"], vkcreds["password"], auth_handler=auth_handler)

try:
    vk_session_audio.auth(token_only = True)
except vk_api.AuthError as error_msg:
    print(error_msg)
    exit()

vkaudio = VkAudio(vk_session_audio)
vk = vk_session.get_api()
print("adding to vk")

def getUserId():
    user_data = vk.users.get()
    user_data = str(user_data[0])
    user_data = dict(ast.literal_eval(user_data))
    user_id = int(user_data['id'])
    return user_id

def createVkPlaylist(playlistName):
    user_id = getUserId()
    vk.audio.createPlaylist(owner_id = user_id, title = playlistName)
    playlists = vk.audio.getPlaylists(owner_id = user_id, count = 1)
    playlists = playlists["items"]
    playlists = dict(playlists[0])
    return int(playlists["id"])

def addAudio(query):
    playlist_id_vk = createVkPlaylist(playlistName)
    tracks = vkaudio.search(q=f"{query}", count=1)
    for n, track in enumerate(tracks, 1):
        vk.audio.add(audio_id = track['id'], owner_id=track['owner_id'], playlist_id = playlist_id_vk)
        print(f'added {query}')

if reverse == True:
    playlist.reverse()


for name in playlist:
    addAudio(name)  