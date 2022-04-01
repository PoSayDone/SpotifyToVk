from time import sleep
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib.request

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

#Your spotify api client_id and client_secret

spotifycreds = {
    "client_id":"id",
    "client_secret":"secret"
}

#False to add from last added to first added tracks

reverse = False

#Id to your playlist
print('Insert Spotify playlist ID')
match_spotify = re.search('([A-Z0-9])\w+', input())
playlist_id = match_spotify.group()

print('Insert VK playlist ID')
match_vk = re.search('_([0-9])\w+_', input())
playlist_id_vk = match_vk.group()
playlist_id_vk = int(playlist_id_vk.replace('_', ''))

creds = SpotifyClientCredentials(client_id = spotifycreds["client_id"], client_secret=spotifycreds["client_secret"])
spotify = spotipy.Spotify(client_credentials_manager=creds)

data = spotify.playlist_tracks(playlist_id=f'{playlist_id}',limit=1, offset=0)

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
    print('Tring to solve captcha...')
    imgURL = captcha.get_url()
    urllib.request.urlretrieve(imgURL, "captcha.png")
    key = vc.solve(image='captcha.png')
#   key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)

def auth_handler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device

playlist = []

for i in range(data['total']):
    artists = getArtists(data)
    name = getName(data)
    data = spotify.playlist_tracks(playlist_id=f'{playlist_id}',limit=1, offset=i)
    playlist.append(f"{artists} - {name}")

vk_session = vk_api.VkApi(vkcreds["login"], vkcreds["password"], auth_handler=auth_handler,captcha_handler=captcha_handler)

try:
    vk_session.auth()
except vk_api.AuthError as error_msg:
    print(error_msg)
    exit()

vkaudio = VkAudio(vk_session)
vk = vk_session.get_api()
print("adding to vk")

def addAudio(query):
    tracks = vkaudio.search(q=f"{query}", count=1)
    for n, track in enumerate(tracks, 1):
        vk.audio.add(audio_id = track['id'], owner_id=track['owner_id'], playlist_id = playlist_id_vk)
        print(f'added {query}')

if reverse == True:
    playlist.reverse()

for name in playlist:
    addAudio(name)  
