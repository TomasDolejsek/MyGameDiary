"""
A library of utilities for communicating with IGDB game database.
"""

import requests
from dotenv import load_dotenv
from os import getenv
from games_app.models import Genre, Perspective, Game
import time


# Environmental variables
load_dotenv(dotenv_path='games_app/.env')
client_id = getenv('CLIENT_ID')
client_secret = getenv('CLIENT_SECRET')
access_token = getenv('ACCESS_TOKEN')


"""
Getting games_app info from IGDB API (using Twitch authentication)
"""

api_url = 'https://api.igdb.com/v4/'


def get_api_token():
    """
    Get new api_token from IGDB API (using Twitch authentication)
    """
    url = 'https://id.twitch.tv/oauth2/token'
    data = {'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'}

    response = requests.post(url, data=data)
    print(response.json())


def get_genres(url=api_url):
    """
    Get list of all game genres
    """
    endpoint = 'genres'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = 'fields id, name; limit 50;'

    response = requests.post(url + endpoint, headers=headers, data=data)
    genres = response.json()
    return genres


def save_genres():
    """
    Save genres to the database
    """
    genres = get_genres()
    for genre in genres:
        id = genre['id']
        name = genre['name']
        new_genre = Genre(id=id, name=name)
        new_genre.save()
    print(f'Successfully saved {len(genres)} genres.')


def get_perspectives(url=api_url):
    """
    Get list of all game perspectives
    """
    endpoint = 'player_perspectives'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f"fields name;"

    response = requests.post(url + endpoint, headers=headers, data=data)
    perspectives = response.json()
    return perspectives


def save_perspectives():
    """
    Save perspectives to the database
    """
    perspectives = get_perspectives()
    for perspective in perspectives:
        id = perspective['id']
        name = perspective['name']
        new_perspective = Perspective(id=id, name=name)
        new_perspective.save()
    print(f'Successfully saved {len(perspectives)} perspectives.')


def find_game_id(name, url=api_url):
    """
    Find a game_id by name
    """
    endpoint = 'games'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields id, name, first_release_date; search "{name}"; limit 100;'

    response = requests.post(url + endpoint, headers=headers, data=data)
    data = response.json()

    games = []
    for game in data:
        if 'first_release_date' not in game:
            continue
        game_data = {}
        game_data['id'] = game['id']
        game_data['name'] = game['name']
        game_data['year'] = convert_to_year(game['first_release_date'])
        games.append(game_data)

    for game in games:
        print(f"id: {game['id']} - '{game['name']}' ({game['year']})")
    return games


def get_game_data(game_id, url=api_url):
    """
    Get relevant game data from IGDB API using game id
    """
    endpoint = 'games'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = (f'fields id, name, cover, first_release_date, rating, summary, genres, player_perspectives; '
            f'where id = {game_id};')

    response = requests.post(url + endpoint, headers=headers, data=data)
    data = response.json()[0]
    if 'player_perspectives' not in data:
        data['player_perspectives'] = []
    if 'rating' not in data:
        data['rating'] = None
    game_data = {'id': data['id'],
                 'name': data['name'],
                 'cover_url': get_game_cover_url(game_id),
                 'year': convert_to_year(data['first_release_date']),
                 'rating': round(data['rating']) if data['rating'] is not None else None,
                 'summary': data['summary'],
                 'genres': data['genres'],
                 'perspectives': data['player_perspectives']}
    return game_data


def save_game(game_id, rewrite=False):
    """
    First, check if game is not already in db, if so rewrite must be set to True to continue
    Get game data from IGDB API using game id and save it to the database
    """
    game_check = Game.objects.filter(pk=game_id).first()
    if game_check and not rewrite:
        print(f'{game_check} already exists in the database.')
        return False
    game_data = get_game_data(game_id)
    game = Game()
    game.id = game_data['id']
    game.name = game_data['name']
    if game.name.startswith('A '):
        game.clear_name = game.name[2:]
    elif game.name.startswith('An '):
        game.clear_name = game.name[3:]
    elif game.name.startswith('The '):
        game.clear_name = game.name[4:]
    else:
        game.clear_name = game.name
    game.cover_url = game_data['cover_url']
    game.year = game_data['year']
    game.rating = game_data['rating']
    game.summary = game_data['summary']
    game.save()
    for genre in game_data['genres']:
        new_genre = Genre.objects.get(pk=genre)
        game.genres.add(new_genre)
    for perspective in game_data['perspectives']:
        new_perspective = Perspective.objects.get(pk=perspective)
        game.perspectives.add(new_perspective)
    game.save()
    print(f'Successfully saved data for {game}.')
    return True


def save_games(rewrite=False):
    """
    Save all games listed in games_id.txt
    """
    count = 0
    with open('games_app/games_id.txt', 'r') as file:
        for game in file.readlines():
            game_id, game_name = game.split(',')
            if save_game(int(game_id), rewrite=rewrite):
                count += 1
    print(f"Successfully saved data of {count} NEW game{'s' if count != 1 else ''}.")


def save_to_file(game_string):
    with open('games_app/games_id.txt', 'a') as file:
        file.write(f"\n{game_string}")
    print('Game credentials saved to file.')


def get_game_cover_url(game_id, url=api_url):
    endpoint = 'covers'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields url; where game = {game_id};'

    response = requests.post(url + endpoint, headers=headers, data=data)
    cover_url = response.json()[0].get('url')
    # print(cover_url)
    return cover_url


def convert_to_year(timestamp):
    """
    Convert timestamp to a year
    """
    return time.gmtime(timestamp).tm_year


"""
Obsolete functions
"""


def get_collection(collection_id, url=api_url):
    endpoint = 'collections'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f"fields name; where id = {collection_id};"

    response = requests.post(url + endpoint, headers=headers, data=data)
    data = response.json()
    return data


def get_franchise(game_id, url=api_url):
    endpoint = 'franchises'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f"fields name; where id = {game_id};"

    response = requests.post(url + endpoint, headers=headers, data=data)
    data = response.json()
    return data


def get_platform_names(platforms_list, url=api_url):
    endpoint = 'platform_families'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f"fields name; limit 20; sort id; where id=6;"
    response = requests.post(url + endpoint, headers=headers, data=data)
    data = response.json()
    print(data)
    return data
