from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView

from core.serializers import UserRegistrationSerializer

User = get_user_model()


class UserRegistrationAPIView(CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        return super().post(request)


"""
import json
from typing import Callable

from django.http import HttpResponse, JsonResponse

from core.errors import SerializerError
from core.models import User
from core.serializers import UserCreateSerializer, UserPublicSerializer


def base_error_handler(func: Callable):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SerializerError as error:
            message = {"errors": error._serializer.errors}
            status_code = 400
        except Exception as error:
            message = {"error": str(error)}
            status_code = 500

        return HttpResponse(
            content_type="application/json",
            content=json.dumps(message),
            status=status_code,
        )

    return inner


@base_error_handler
def user_router(request):
    if request.method == "POST":
        return create_user(request)
    elif request.method == "GET":
        return retrieve_user(request)


def create_user(request):
    create_serializer = UserCreateSerializer(data=json.loads(request.body))

    is_valid = create_serializer.is_valid()
    if not is_valid:
        raise SerializerError(create_serializer)

    user = User.objects.create_user(**create_serializer.validated_data)

    user_public_serializer = UserPublicSerializer(user)
    return JsonResponse(user_public_serializer.data)


def retrieve_user(request):
    user = User.object.get()
    user_public_serializer = UserPublicSerializer(user)

    return JsonResponse(user_public_serializer.data)
"""
