from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import base64
import json

access_token = 'BQDAP9FCoLE96LUprlBGFHlaIJp0jkZavuJB3_ws7Su7qtt3eIijRHmzzjMUkC-C2SidtBnfy6gguUpottg'

def home(request):
    return render(request, 'home.html')

def top(request):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }


    url = "https://www.melon.com/chart/index.htm"
    melons = [
        {
            'track': song.select_one(' div.wrap div.wrap_song_info .rank01 a').text.strip(),
            'album': song.select_one(' div.wrap div.wrap_song_info .rank03 a').text.strip(),
            'image': song.select_one('div.wrap a.image_typeAll > img')['src'].strip(),
            'artist': song.select_one(' div.wrap div.wrap_song_info .rank02 a').text.strip()
        }
        for song in BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser').select('div.d_song_list table tbody tr')
    ]
    return render(request, 'top.html', {'melons': melons})

def song_detail(request, song):
    pass

def search(request):
    global access_token
    type = request.GET.get('type')
    item = request.GET.get('item')

    req = requests.get(f'https://api.spotify.com/v1/search?query={item}&type={type}&access_token='+access_token)
    if req.status_code != 200:
        client_id = "05bb41a7d2c246ee969af53ccc2b1e8f"
        client_key = '5f7dea92f9aa4b7aa9fe0917d848ebd7'
        endpoint = 'https://accounts.spotify.com/api/token'

        encoded = base64.b64encode("{}:{}".format(client_id, client_key).encode('utf-8')).decode('ascii')

        headers = {"Authorization": 'Basic {}'.format(encoded)}
        payload = {'grant_type': 'client_credentials'}

        response = requests.post(endpoint, data=payload, headers=headers)
        access_token = json.loads(response.text)['access_token']
        req = requests.get(f'https://api.spotify.com/v1/search?query={item}&type={type}&access_token='+access_token)

    data = req.json()

    context = {}
    if type=='album':
        artistget = request.GET.get('artist')
        req2 = requests.get(f'https://api.spotify.com/v1/search?query={artistget}&type=artist&access_token='+access_token)
        if req2.status_code != 200:
            client_id = "05bb41a7d2c246ee969af53ccc2b1e8f"
            client_key = '5f7dea92f9aa4b7aa9fe0917d848ebd7'
            endpoint = 'https://accounts.spotify.com/api/token'

            encoded = base64.b64encode("{}:{}".format(client_id, client_key).encode('utf-8')).decode('ascii')

            headers = {"Authorization": 'Basic {}'.format(encoded)}
            payload = {'grant_type': 'client_credentials'}

            response = requests.post(endpoint, data=payload, headers=headers)
            access_token = json.loads(response.text)['access_token']
            req2 = requests.get(f'https://api.spotify.com/v1/search?query={artistget}&type=artist&access_token='+access_token)
        data2 = req2.json()
        d =  [album for album in data['albums']['items'] for artist in album['artists'] if artist['id'] in [d['id'] for d in data2['artists']['items']]][0]
        context['image'] = d['images'][1]['url']
        context['image_small'] = d['images'][2]['url']
        context['name'] = d['name']
        context['artist'] = ','.join([artist['name'] for artist in d['artists']])
        context['tracks'] = requests.get('https://api.spotify.com/v1/albums/' + data['albums']['items'][0]['id'] + '/tracks?access_token='+access_token).json()['items']
    elif type=='artist':
        d = data['artists']['items'][0]
        req2 = requests.get(f'https://api.spotify.com/v1/artists/{d["id"]}/top-tracks?market=KR&access_token={access_token}')
        if req2.status_code != 200:
            client_id = "05bb41a7d2c246ee969af53ccc2b1e8f"
            client_key = '5f7dea92f9aa4b7aa9fe0917d848ebd7'
            endpoint = 'https://accounts.spotify.com/api/token'

            encoded = base64.b64encode("{}:{}".format(client_id, client_key).encode('utf-8')).decode('ascii')

            headers = {"Authorization": 'Basic {}'.format(encoded)}
            payload = {'grant_type': 'client_credentials'}

            response = requests.post(endpoint, data=payload, headers=headers)
            access_token = json.loads(response.text)['access_token']
            req2 = requests.get(f'https://api.spotify.com/v1/artists/{d["id"]}/top-tracks?market=KR&access_token={access_token}')
        data2 = req2.json() 
        context['image'] = d['images'][1]['url']
        context['name'] = d['name']
        context['genre'] = d['genres']
        context['tracks'] = data2['tracks']
    elif type=='track':
        artistget = request.GET.get('artist')
        req2 = requests.get(f'https://api.spotify.com/v1/search?query={artistget}&type=artist&access_token='+access_token)
        if req2.status_code != 200:
            client_id = "05bb41a7d2c246ee969af53ccc2b1e8f"
            client_key = '5f7dea92f9aa4b7aa9fe0917d848ebd7'
            endpoint = 'https://accounts.spotify.com/api/token'

            encoded = base64.b64encode("{}:{}".format(client_id, client_key).encode('utf-8')).decode('ascii')

            headers = {"Authorization": 'Basic {}'.format(encoded)}
            payload = {'grant_type': 'client_credentials'}

            response = requests.post(endpoint, data=payload, headers=headers)
            access_token = json.loads(response.text)['access_token']
            req2 = requests.get(f'https://api.spotify.com/v1/search?query={artistget}&type=artist&access_token='+access_token)
        data2 = req2.json()
        d = [track for track in data['tracks']['items'] for ar in track['artists'] if ar['id'] in [d['id'] for d in data2['artists']['items']]][0]
        context['album'] = d['album']['name']
        context['release'] = d['album']['release_date']
        context['image'] = d['album']['images'][1]['url']
        context['name'] = d['name']
        context['artist'] = ", ".join([arts['name'] for arts in d['artists']])
        context['artists'] = d['artists']

    return render(request, f'{type}.html',{'data': context})

