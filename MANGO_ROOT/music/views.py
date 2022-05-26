from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pymysql
import pymysql.cursors
import time
import os

def home(request):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
    }


    url = "https://www.melon.com/chart/index.htm"
    melons = [
        {
            'title': song.select_one(' div.wrap div.wrap_song_info .rank01 a').text.strip(),
            'album': song.select_one(' div.wrap div.wrap_song_info .rank03 a').text.strip(),
            'image': song.select_one('div.wrap a.image_typeAll > img')['src'].strip(),
            'artist': song.select_one(' div.wrap div.wrap_song_info .rank02 a').text.strip()
        }
        for song in BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser').select('div.d_song_list table tbody tr')
    ]
    return render(request, 'home.html', {'melons': melons})


def song_detail(request, song):
    pass
