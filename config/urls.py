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
import requests

from dataclasses import dataclass, asdict

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def filter_by_keys(source:dict, keys: list[str]) -> dict:
    filtered_data = {}
    for key,value in source.items():
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
        cls.__dataclass_fields__.keys()
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


def get_pokemon(request, name):
    pokemon: Pokemon = _get_pokemon(name)
    return HttpResponse(
        content_type="application/json", content=json.dumps(asdict(pokemon))
    )


def get_pokemon_on_mobile(request, name):
    pokemon: Pokemon = _get_pokemon(name)
    
    only_fields = ("id", "name", "base_experience")
    result = filter_by_keys(asdict(pokemon), only_fields)

    return HttpResponse(
        content_type="application/json", content=json.dumps(result)
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/pokemon/<str:name>/", get_pokemon),
    path("api/mobile/pokemon/<str:name>/", get_pokemon_on_mobile),
]
