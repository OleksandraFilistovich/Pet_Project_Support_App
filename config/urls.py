"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import json
from dataclasses import asdict, dataclass
from random import choice, randint
from string import ascii_letters

import requests
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from core.models import User


def filter_by_keys(source: dict, keys: list[str]) -> dict:
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
        filtered_data = filter_by_keys(
            raw_data,
            cls.__dataclass_fields__.keys(),
        )
        return cls(**filtered_data)


POKEMONS: dict[str, Pokemon] = {}


def get_pokemon_from_api(name: str) -> Pokemon:
    url = settings.POKEAPI_BASE_URL + f"/{name}"
    response = requests.get(url)
    data = response.json()

    return Pokemon.from_raw_data(data)


def _get_pokemon(name) -> Pokemon:
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


@csrf_exempt
def differ_request_method(request, name):
    if request.method == "GET":
        return _get_pokemon_response(name)
    if request.method == "DELETE":
        return _delete_pokemon_response(name)


def _get_pokemon_response(name):
    pokemon: Pokemon = _get_pokemon(name)
    return HttpResponse(
        content_type="application/json", content=json.dumps(asdict(pokemon))
    )


def _delete_pokemon_response(name):
    if name in POKEMONS:
        del POKEMONS[name]
        return HttpResponse(f"<p>Deleted {name} successfully.</p>")
    else:
        return HttpResponse(f"<p>{name} pokemon isn't cached.</p>")


def get_pokemon_on_mobile(request, name):
    pokemon: Pokemon = _get_pokemon(name)

    only_fields = ("id", "name", "base_experience")
    result = filter_by_keys(asdict(pokemon), only_fields)

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(result),
    )


def get_all_pokemon(request):
    pokemons_list = []
    for value in POKEMONS.values():
        pokemons_list.append(asdict(value))

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(pokemons_list),
    )


# *****************************************************
# All roles are hardcoded instead of beeing used in the database
# *****************************************************
ROLES = {
    "ADMIN": 1,
    "MANAGER": 2,
    "USER": 3,
}


def _get_random_string(size: int = 5) -> str:
    return "".join([choice(ascii_letters) for _ in range(size)])


def create_random_user(request):
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


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/pokemon/", get_all_pokemon),
    path("api/pokemon/<str:name>/", differ_request_method),
    path("api/pokemon/mobile/<str:name>/", get_pokemon_on_mobile),
    path("create-random-user/", create_random_user),
]
