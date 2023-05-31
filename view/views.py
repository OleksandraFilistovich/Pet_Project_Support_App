# from django.shortcuts import render

import json
from dataclasses import asdict, dataclass
from random import choice, randint
from string import ascii_letters

import requests
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from core.models import User

# * VARIABLES AND NEEDED DICTS *
# Cache simulated by storing pokemons in this dict
POKEMONS: dict[str, "Pokemon"] = {}
# All roles are hardcoded instead of beeing used in the database
ROLES = {
    "ADMIN": 1,
    "MANAGER": 2,
    "USER": 3,
}


def filter_by_keys(source: dict, keys: list[str]) -> dict:
    """
    Returns given dict filtered by list of fields/keys.
    """
    filtered_data = {}
    for key, value in source.items():
        if key in keys:
            filtered_data[key] = value
    return filtered_data


@dataclass
class Pokemon:
    id: int
    name: str
    weight: int
    height: int
    base_experience: int

    @classmethod
    def from_raw_data(cls, raw_data: dict) -> "Pokemon":
        """
        Filter raw pokemon response to our data structure.
        """
        filtered_data = filter_by_keys(
            raw_data,
            cls.__dataclass_fields__.keys(),
        )
        return cls(**filtered_data)


def get_pokemon_from_api(name: str) -> Pokemon:
    """
    Connects to API and returns Pokemon object with given name.
    """
    url = settings.POKEAPI_BASE_URL + f"/{name}"
    response = requests.get(url)
    data = response.json()

    return Pokemon.from_raw_data(data)


def _get_pokemon(name: str) -> Pokemon:
    """
    Take pokemon from the cache or
    fetch it from the API and save to the cache.
    """
    if name in POKEMONS:
        pokemon = POKEMONS[name]
    else:
        pokemon: Pokemon = get_pokemon_from_api(name)
        POKEMONS[name] = pokemon
    return pokemon


# * decorator lets anybody send any requests without security checks
@csrf_exempt
def differ_request_method(request, name: str) -> HttpResponse:
    if request.method == "GET":
        return _get_pokemon_response(name)
    if request.method == "DELETE":
        return _delete_pokemon_response(name)


def _get_pokemon_response(name: str) -> HttpResponse:
    """Returns json with requested pokemon."""
    pokemon: Pokemon = _get_pokemon(name)
    return HttpResponse(
        content_type="application/json", content=json.dumps(asdict(pokemon))
    )


def _delete_pokemon_response(name: str) -> HttpResponse:
    """Checks existense then deletes if possible."""
    if name in POKEMONS:
        del POKEMONS[name]
        return HttpResponse(f"<p>Deleted {name} successfully.</p>")
    else:
        return HttpResponse(f"<p>{name} pokemon isn't cached.</p>")


def get_pokemon_on_mobile(request, name: str) -> HttpResponse:
    """Smaller json response on GET pokemon."""
    pokemon: Pokemon = _get_pokemon(name)

    only_fields = ("id", "name", "base_experience")
    result = filter_by_keys(asdict(pokemon), only_fields)

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(result),
    )


def get_all_pokemon(request) -> HttpResponse:
    """Returns json dict with all cached Pokemons."""
    pokemons_list = []
    for value in POKEMONS.values():
        pokemons_list.append(asdict(value))

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(pokemons_list),
    )


def _get_random_string(size: int = 5) -> str:
    return "".join([choice(ascii_letters) for _ in range(size)])


def create_random_user(request) -> HttpResponse:
    """Creates new user to database in Users table"""

    name = _get_random_string(size=randint(5, 10))
    email_af = _get_random_string(size=randint(2, 4)).lower()
    email_domain = choice(["net", "com", "io"])
    email_full = "".join([name, "@", email_af, ".", email_domain])

    random_user = User.objects.create(
        username=name,
        email=email_full,
        first_name=_get_random_string(size=randint(5, 10)),
        last_name=_get_random_string(size=randint(5, 10)),
        role=ROLES["USER"],
        password=_get_random_string(size=randint(10, 20)),
    )
    result = {
        "id": random_user.pk,
        "username": random_user.username,
        "email": random_user.email,
        "firstName": random_user.first_name,
        "lastName": random_user.last_name,
        "role": random_user.role,
        "password": random_user.password,
    }

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(result),
    )
