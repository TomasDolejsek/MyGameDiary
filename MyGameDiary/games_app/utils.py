import requests
from dotenv import load_dotenv
from os import getenv
from games_app.models import *


# Environmental variables
load_dotenv()
client_id = getenv('CLIENT_ID')
client_secret = getenv('CLIENT_SECRET')
access_token = getenv('ACCESS_TOKEN')


"""
Getting games info from IGDB API (using Twitch authentication)
"""

api_url = 'https://api.igdb.com/v4/'


def get_api_token():
    url = 'https://id.twitch.tv/oauth2/token'
    data = {'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'}

    response = requests.post(url, data=data)
    print(response.json())


def get_genres(url=api_url):
    endpoint = 'genres'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = 'fields id, name; limit 50;'

    response = requests.post(url + endpoint, headers=headers, data=data)
    genres = response.json()
    return genres


def save_genres():
    genres = get_genres()
    for genre in genres:
        id = genre['id']
        name = genre['name']
        new_genre = Genre(id=id, name=name)
        new_genre.save()
    print(f'Successfully saved {len(genres)} genres.')


def find_game_id(name, url=api_url):
    endpoint = 'games'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields id, name; search "{name}";'

    response = requests.post(url + endpoint, headers=headers, data=data)
    print(response.json())


def get_game_data(game_id, url=api_url):
    endpoint = 'games'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields id, name, genres; where id = {game_id};'

    response = requests.post(url + endpoint, headers=headers, data=data)
    data = response.json()[0]
    game_data = {'api_id': data['id'],
                 'name': data['name'],
                 'year': get_game_release_year(game_id),
                 'cover_url': get_game_cover_url(game_id),
                 'genres': data['genres']}
    return game_data


def save_games():
    count = 0
    with open('games_id.txt', 'r') as file:
        for game_id in file.readlines():
            count += 1
            save_game(int(game_id))
    print(f'Successfully saved data of {count} games.')


def save_game(game_id):
    game_data = get_game_data(game_id)
    game = Game()
    game.api_id = game_data['api_id']
    game.name = game_data['name']
    game.year = game_data['year']
    game.cover_url = game_data['cover_url']
    game.save()
    for genre in game_data['genres']:
        new_genre = Genre.objects.get(pk=genre)
        game.genres.add(new_genre)
    game.save()
    print(f'Successfully saved data for {game.name} (api_id: {game.api_id}).')


def get_game_cover_url(game_id, url=api_url):
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields url; where game = {game_id};'

    response = requests.post(url + 'covers', headers=headers, data=data)
    cover_url = response.json()[0].get('url')
    # print(cover_url)
    return cover_url


def get_game_release_year(game_id, url=api_url):
    endpoint = 'release_dates'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields y; where game = {game_id};'

    response = requests.post(url + endpoint, headers=headers, data=data)
    year = min([x.get('y') for x in response.json()])
    # print(year)
    return year
