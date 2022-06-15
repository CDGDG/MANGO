from django.http import JsonResponse
from django.shortcuts import render
from matplotlib.pyplot import get
import requests
from bs4 import BeautifulSoup
import base64
import json
from user.views import getLyrics

# 재학습 
import pandas as pd
import os
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



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

def search(request):
    global access_token
    type = request.GET.get('type')
    item = request.GET.get('item')

    context = {}
    try:
        if type=='album':
            artistget = request.GET.get('artist')
            melon_data = getMelonAlbum(item, artistget)
            print(melon_data)
            context['image'] = melon_data['image']
            context['image_small'] = melon_data['image_small']
            context['name'] = melon_data['name']
            context['artist'] = melon_data['artist']
            context['tracks'] = melon_data['tracks']
        elif type=='artist':
            melon_data = getMelonArtist(item)
            print(melon_data)
            context['image'] = melon_data['image']
            context['name'] = melon_data['name']
            context['tracks'] = melon_data['tracks']
        elif type=='track':
            artistget = request.GET.get('artist')
            melon_data = getMelonInfo(item, artistget)
            context['album'] = melon_data['album']
            context['release'] = melon_data['release']
            context['image'] = melon_data['image']
            context['name'] = melon_data['name']
            context['artist'] = melon_data['artist']
            context['artists'] = melon_data['artist']
            context['lyrics'] = melon_data['lyrics']
    except IndexError as ie:
        context['error'] = 'IndexError'

    return render(request, f'{type}.html',{'data': context})

def recommend(request, query):
    return JsonResponse({'data': query})

def getMelonInfo(track, artist):
    track2 = track.replace('953964', '&amp;')
    query = f'{track2} {artist}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }
    q_url = 'https://www.melon.com/search/song/index.htm?q='+query
    try:
        trackid = BeautifulSoup(requests.get(q_url, headers=headers).text, 'html.parser').select_one('table tbody tr td div.wrap.pd_none.left input')['value']
        url = 'https://www.melon.com/song/detail.htm?songId='+trackid
        soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
        data = {
            'album': soup.select_one('dl.list > dd').text.strip(),
            'release': soup.select('dl.list > dd')[1].text.strip(),
            'image': soup.select_one('div.wrap_info > div.thumb > a > img')['src'].strip(),
            'name': soup.select_one('div.info > div.song_name').text.replace('곡명', '').strip(),
            'artist': soup.select_one('div.info > div.artist > a.artist_name > span').text.strip(),
            'lyrics': BeautifulSoup(str(soup.select_one('#d_video_summary')).replace('<br/>', '\n'), 'html.parser').text.split('\n'),
            }
    except Exception as e:
        return ('곡 정보 불러오기 실패', e)
    return data

def getMelonArtist(artist):
    q_url = 'https://www.melon.com/search/artist/index.htm?q='+artist
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }
    data = {}
    try:
        artistid = BeautifulSoup(requests.get(q_url, headers=headers).text, 'html.parser').select_one('#pageList .d_artist_list ul li .wrap_atist12 button.btn_join_fan')['data-artist-no']
        url = f"https://www.melon.com/artist/song.htm?artistId={artistid}#params%5BorderBy%5D=POPULAR_SONG_LIST&params%5B"
        soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
        data['image'] = soup.select_one('#artistImgArea img').get('src')
        data['name'] = soup.select_one('.title_atist').text.replace('아티스트명', '')
        data['tracks'] = [{
            'title': tr.select_one('.ellipsis a.fc_gray').text,
            'artist': tr.select_one('#artistName a.fc_mgray').text,
            'album': tr.select_one('.ellipsis:not(#artistName) a.fc_mgray').text,
        }
        for tr in soup.select('#frm div.tb_list.d_song_list.songTypeOne table tbody tr')]
    except Exception as e:
        return ('아티스트 정보 불러오기 실패', e)
    return data


def getMelonAlbum(album, artist):
    album2 = album.replace('953964', '&amp;')
    query = f'{album2} {artist}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }
    q_url = 'https://www.melon.com/search/album/index.htm?q='+query
    try:
        soup = BeautifulSoup(requests.get(q_url, headers=headers).text, 'html.parser').select_one('#frm ul.album11_ul li.album11_li div.wrap_album04')
        albumid = soup.select_one('dd.wrap_btn > a')['data-album-no']
        albumsoup = BeautifulSoup(requests.get('https://www.melon.com/album/detail.htm?albumId='+albumid, headers=headers).text, 'html.parser')
        data = {}
        data['image'] = soup.select_one('a.thumb > img')['src'].strip()
        data['image_small'] = soup.select_one('a.thumb > img')['src'].replace('/260/', '/120/').strip()
        data['name'] = soup.select_one('div.atist_info > dl > dt > a.ellipsis').text.strip()
        data['artist'] = soup.select_one('div.atist_info dd.atistname > div.ellipsis > a').text.strip()
        data['tracks'] = [{
            'name': tr.select_one('div.wrap_song_info div.ellipsis span a').text.strip(),
            'artist': tr.select_one('div.wrap_song_info div.ellipsis.rank02 a').text.strip(),
            } for tr in albumsoup.select('#frm table tbody tr:not(.cd)')]
    except Exception as e:
        return ('앨범 정보 불러오기 실패', e, data)
    return data

def searchlist(request, track):
    context = {}
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }
    print(track+'로 음악 검색')
    url = "https://www.melon.com/search/total/index.htm?q="+track
    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
    # 아티스트 있는지 확인
    artistsoup = soup.select_one('.section_atist div.wrap_cntt.clfix.d_artist_list')
    if artistsoup and artistsoup.select_one('a.wrap_thumb > img'):
        context['artist'] = {
            'image': soup.select_one('a.wrap_thumb > img').get('src'),
            'name': soup.select_one('.atist_dtl_info .fc_serch').text.strip(),
            }
    context['tracks'] = [
                            {
                                'track': BeautifulSoup(str(searchs.select_one('td div.ellipsis a.fc_gray')).replace('<b>','').replace('</b>',""), 'html.parser').text,
                                'artist': searchs.select_one('#artistName span').text,
                            }
                            for searchs in soup.select('#frm_searchSong table tbody tr')
                        ][:3]

    return JsonResponse({'data': context})

def update_data(request):
    query = request.GET.get('query')
    intent = request.GET.get('intent')
    data = pd.DataFrame([query],columns = ['sentence'])
    data['label'] = intent
    print("===================",query,intent,"=================================")
    retrain_file = 'static/retrain_data/retrain_data.csv'
    try:
        retrain_data = pd.read_csv(retrain_file)
    except:
        data.to_csv(r'./static/retrain_data/retrain_data.csv')
        context = {'data':"성공"}
        return JsonResponse(context)
  
    result = pd.concat([retrain_data,data])
    result.to_csv(r'./static/retrain_data/retrain_data.csv',index=False)
    context = {'data':"성공"}

    return JsonResponse(context)
