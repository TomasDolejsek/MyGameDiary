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


def get_perspectives(url=api_url):
    endpoint = 'player_perspectives'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f"fields name;"

    response = requests.post(url + endpoint, headers=headers, data=data)
    perspectives = response.json()
    return perspectives


def save_perspectives():
    perspectives = get_perspectives()
    for perspective in perspectives:
        id = perspective['id']
        name = perspective['name']
        new_perspective = Perspective(id=id, name=name)
        new_perspective.save()
    print(f'Successfully saved {len(perspectives)} perspectives.')


def find_game_id(name, url=api_url):
    endpoint = 'games'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields id, name; search "{name}"; limit 100;'

    response = requests.post(url + endpoint, headers=headers, data=data)
    games = response.json()
    print(len(games))
    for game in games:
        print(f"id: {game['id']} - '{game['name']}'")
    return games


def get_game_data(game_id, url=api_url):
    endpoint = 'games'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = (f'fields id, name, cover, first_release_date, rating, summary, genres, player_perspectives; '
            f'where id = {game_id};')

    response = requests.post(url + endpoint, headers=headers, data=data)
    data = response.json()[0]
    if 'player_perspectives' not in data:
        data['player_perspectives'] = []
    game_data = {'id': data['id'],
                 'name': data['name'],
                 'cover_url': get_game_cover_url(game_id),
                 'year': convert_to_year(data['first_release_date']),
                 'rating': round(data['rating']),
                 'summary': data['summary'],
                 'genres': data['genres'],
                 'perspectives': data['player_perspectives']}
    return game_data


def save_game(game_id, rewrite=False):
    game_check = Game.objects.filter(pk=game_id).first()
    if game_check and not rewrite:
        print(f'{game_check} already exists in the database.')
        return False
    game_data = get_game_data(game_id)
    game = Game()
    game.id = game_data['id']
    game.name = game_data['name']
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
    return time.gmtime(timestamp).tm_year


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



