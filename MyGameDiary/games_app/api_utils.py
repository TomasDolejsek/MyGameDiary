"""
A library of utilities for communicating with IGDB game database.
"""

import requests
from dotenv import load_dotenv
from os import getenv
from games_app.models import Genre, Perspective, Franchise, Game
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
        game_data = {
            'id': game['id'],
            'name': game['name'],
            'year': convert_to_year(game['first_release_date'])
        }
        print(f"id: {game_data['id']} - '{game_data['name']}' ({game_data['year']})")
        games.append(game_data)

    return games


def get_game_data(game_id, url=api_url):
    """
    Get relevant game data from IGDB API using game id
    """
    endpoint = 'games'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = (f'fields id, name, cover, first_release_date, total_rating, summary, franchises, '
            f'genres, player_perspectives; where id = {game_id};')

    response = requests.post(url + endpoint, headers=headers, data=data)
    data = response.json()[0]
    if 'franchises' not in data:
        data['franchises'] = []
    if 'player_perspectives' not in data:
        data['player_perspectives'] = []
    if 'total_rating' not in data:
        data['total_rating'] = None
    game_data = {'id': data['id'],
                 'name': data['name'],
                 'cover_url': get_game_cover_url(game_id),
                 'year': convert_to_year(data['first_release_date']),
                 'rating': round(data['total_rating']) if data['total_rating'] is not None else None,
                 'summary': data['summary'],
                 'franchise_id': data['franchises'][0] if data['franchises'] else None,
                 'genres': data['genres'],
                 'perspectives': data['player_perspectives']}
    return game_data


def get_clear_name(name):
    if name.startswith('A '):
        clear_name = name[2:]
    elif name.startswith('An '):
        clear_name = name[3:]
    elif name.startswith('The '):
        clear_name = name[4:]
    else:
        clear_name = name
    return clear_name


def save_ordering_names():
    games = Game.objects.all()
    count = 0
    for game in games:
        count += 1
        game.set_ordering_name()
        game.save()
    print(f"Successfully saved {count} ordering_name{'s' if count != 1 else ''}.")


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
    game.cover_url = game_data['cover_url']
    game.year = game_data['year']
    game.rating = game_data['rating']
    game.summary = game_data['summary']
    franchise = None
    if game_data['franchise_id']:
        franchise, created = Franchise.objects.get_or_create(
            id=game_data['franchise_id'],
            name=get_franchise_name(game_data['franchise_id'])
        )
    game.franchise = franchise
    game.save()
    for genre in game_data['genres']:
        new_genre = Genre.objects.get(pk=genre)
        game.genres.add(new_genre)
    for perspective in game_data['perspectives']:
        new_perspective = Perspective.objects.get(pk=perspective)
        game.perspectives.add(new_perspective)
    game.set_ordering_name()
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
    return cover_url


def get_game_franchise_id(game_id, url=api_url):
    endpoint = 'games'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields franchises; where id = {game_id};'
    response = requests.post(url + endpoint, headers=headers, data=data)
    franchise_id = response.json()[0].get('franchises')
    return franchise_id[0] if franchise_id else None


def get_franchise_name(franchise_id, url=api_url):
    endpoint = 'franchises'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f"fields name; where id = {franchise_id};"

    response = requests.post(url + endpoint, headers=headers, data=data)
    franchise_name = response.json()[0].get('name')
    return franchise_name


def get_game_franchise_name(game_id):
    franchise_id = get_game_franchise_id(game_id)
    if not franchise_id:
        return None
    franchise_name = get_franchise_name(franchise_id)
    return franchise_name


def save_franchise(franchise_id):
    franchise_check = Franchise.objects.filter(id=franchise_id).first()
    if franchise_check:
        print(f'{franchise_check} already exists in the database.')
        return False
    franchise = Franchise.objects.create(id=franchise_id, name=get_franchise_name(franchise_id))
    print(f'Successfully saved data for {franchise}.')
    return True


def convert_to_year(timestamp):
    """
    Convert timestamp to a year
    """
    return time.gmtime(timestamp).tm_year


def find_and_save_games_franchises(update=False):
    games = Game.objects.all()
    count = 0
    for game in games:
        print(f'Checking {game} franchise...')
        if game.franchise is not None and not update:
            print(f"Franchise '{game.franchise_text}' already set for {game}. Skipping...")
            continue
        franchise_id = get_game_franchise_id(game.id)
        if not franchise_id:
            game.franchise = None
        else:
            count += 1
            game.franchise, created = Franchise.objects.get_or_create(
                id=franchise_id,
                name=get_franchise_name(franchise_id)
            )
        game.save()
        print(f"Found '{game.franchise_text}' franchise for {game}.")
        game.set_ordering_name()
        game.save()
        print(f"Ordering_name '{game.ordering_name}' set for {game}.")
    print(f"Successfully saved {count} franchise{'s' if count != 1 else ''}.")


def check_franchise_exists(franchise_name, url=api_url):
    endpoint = 'franchises'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields id, name; where name = "{franchise_name}";'
    response = requests.post(url + endpoint, headers=headers, data=data)
    exists = f"{response.json()[0].get('id')}: {franchise_name}" if response.json() \
             else f"{franchise_name} franchise not found."
    return exists


def get_game_total_rating(game_id, url=api_url):
    endpoint = 'games'
    headers = {'Client-ID': client_id,
               'Authorization': 'Bearer ' + access_token}
    data = f'fields total_rating; where id = {game_id};'
    response = requests.post(url + endpoint, headers=headers, data=data)
    total_rating = response.json()[0].get('total_rating')
    return round(total_rating) if total_rating else None


def update_ratings():
    games = Game.objects.all()
    count = 0
    for game in games:
        old_rating = game.rating
        new_rating = get_game_total_rating(game.id)
        if new_rating != old_rating:
            count += 1
            game.rating = new_rating
            game.save()
            print(f"Rating for {game} has been updated. {old_rating} -> {new_rating}")
    print(f"Successfully updated {count} rating{'s' if count != 1 else ''}.")
