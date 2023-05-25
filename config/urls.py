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
from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def get_pokemon(request, name):
    url = settings.POKEAPI_BASE_URL + f"/{name}"
    response = requests.get(url)
    data = response.json()

    pokemon_info = {
        "id": data["id"],
        "name": data["name"],
        "height": data["height"],
        "weight": data["weight"],
        "baseExperience": data["base_experience"],
    }

    return HttpResponse(
        content_type="application/json", content=json.dumps(pokemon_info)
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/pokemon/<name>", get_pokemon),
]
