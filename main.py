from asyncio.windows_events import NULL
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import ast
from vkaudiotoken import get_vk_official_token
import os.path
from time import sleep
import sys
import urllib
import json

import vk_captchasolver as vc
import re
import vk_api
from vk_api.audio import VkAudio

with open("account_data.json") as jsonFile:
    jsonAccData = json.load(jsonFile)
    jsonFile.close()

#Getting VK Audio Token
if os.path.exists('vk_audio_token.txt'):
    file = open("vk_audio_token.txt")
    vk_audio_token = file.readline()
    file.close
else:
    file_w = open("vk_audio_token.txt", "w")
    vk_audio_token = get_vk_official_token(jsonAccData["vkLogin"], jsonAccData["vkPassword"])
    vk_audio_token = vk_audio_token["token"]
    file_w.write(str(vk_audio_token))
    file_w.close

#True to add from last added to first added tracks
reverse = True

#Id to your playlist
print('Insert Spotify playlist link')
match_spotify = re.search('([A-Z0-9])\w+', input())
playlist_id = match_spotify.group()

creds = SpotifyClientCredentials(client_id = jsonAccData["spotifyId"], client_secret=jsonAccData["spotifySecret"])
spotify = spotipy.Spotify(client_credentials_manager=creds)

results = spotify.user_playlist(user=None, playlist_id=f'{playlist_id}', fields="name")
data = spotify.playlist_items(playlist_id=f'{playlist_id}')

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

def autoCaptchaHandler(captcha):
    print('Trying to solve captcha...')
    imgURL = captcha.get_url()
    urllib.request.urlretrieve(imgURL, "captcha.png")
    key = vc.solve(image='captcha.png')
    return captcha.try_again(key)

def captchaHandler(captcha):
    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()
    return captcha.try_again(key)

def authHandler():
    key = input("Enter authentication code: ")
    remember_device = True
    return key, remember_device

print('Choose captcha handler. a - for auto, m - for manual')

while True:
    captcha_state = input()
    if captcha_state == 'a':
        break
    elif captcha_state == 'm':
        break
    else:
        print('You entered an invalid value, please try again')
        continue

playlistName = getPlaylistName(results)

playlist = []

for i in range(1, data['total']+1):
    artists = getArtists(data)
    name = getName(data)
    data = spotify.playlist_tracks(playlist_id=f'{playlist_id}',limit=1, offset=i)
    playlist.append(f"{artists} - {name}")

if captcha_state == 'a':
    vk_session = vk_api.VkApi(token = vk_audio_token, captcha_handler = autoCaptchaHandler)
else:
    vk_session = vk_api.VkApi(token = vk_audio_token, captcha_handler = captchaHandler)

vk_session_audio = vk_api.VkApi(jsonAccData["vkLogin"], jsonAccData["vkPassword"], auth_handler=authHandler)

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
    vk.audio.createPlaylist(owner_id = user_id, title = playlistName)
    print(playlistName)

def getVkPlaylistName():
    playlists = vk.audio.getPlaylists(owner_id = user_id, count = 1)
    playlists = playlists["items"]
    playlists = dict(playlists[0])
    return int(playlists["id"])

def addAudio(query):
    tracks = vkaudio.search_iter(q=f"{query}")
    for track in tracks:
        vk.audio.add(audio_id = track['id'], owner_id=track['owner_id'], playlist_id = playlist_id_vk)
        if track['id'] != None: return True
    
user_id = getUserId()
createVkPlaylist(playlistName)
playlist_id_vk = getVkPlaylistName()

if reverse == True:
    playlist.reverse()

not_found = []

for name in playlist:
    sys.stderr.write(f'Adding {name}\r')
    sleep(.5)
    added_song = addAudio(name)  
    if added_song == None:
        not_found.append(f"{name}")
        print(f'Not added {name} ❌')
    else: 
        print(f'Added {name} ✅')
if not not_found:
    print("All tracks was successfully added")
else:
    print("Not Found:")
    for i in range(len(not_found)):
        print('❌ ', not_found[i])
