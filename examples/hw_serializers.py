import json
from random import choice
from string import ascii_letters

from core.errors import SerializerError
from django.contrib.auth import authenticate, get_user_model
from django.http import HttpResponse
from rest_framework import serializers

User = get_user_model()


# ===== HOMEWORK =====
class UserCreateRequestSerializer(serializers.Serializer):
    """
    Processing data in create_user request
    with ALL data.
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    first_name = serializers.CharField()
    last_name = serializers.CharField()


class UserCreateResponseSerializer(serializers.ModelSerializer):
    """
    Data we send back after complite registration.
    """

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role"]


class LoginRequestSerializer(serializers.Serializer):
    """
    Processing data needed to log in.
    """

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            message_login_request = "Log in is successful!"
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )
            if not user:
                message_login_request = "Can't log in."
        else:
            message_login_request = "Can't log in."

        data["user"] = user
        data["log_message"] = message_login_request
        return data


class LoginResponseSerializer(serializers.ModelSerializer):
    """
    Response data to log in request.
    """

    class Meta:
        model = User
        fields = ["id", "email"]


# ===== TEST HW SERIALIZERS =====
def test_serializers(request):
    # request for testing create serializer
    name = "".join([choice(ascii_letters) for _ in range(5)])
    email = f"{name}@email.com"
    request_create = {
        "email": email,
        "password": "12345678",
        "first_name": "Alex",
        "last_name": "Filistovich",
    }

    # validation of data
    create_serializer = UserCreateRequestSerializer(data=request_create)
    is_valid_create = create_serializer.is_valid()
    if not is_valid_create:
        raise SerializerError(create_serializer)

    # user creating
    user = User.objects.create_user(**create_serializer.validated_data)

    # converting user data back
    user_public_serializer = UserCreateResponseSerializer(user)
    public_create = dict(user_public_serializer.data)

    # request for testing log in serializer
    request_login = {"email": email, "password": "12345678"}

    # validation of data and checking user & password inside serializer
    login_serializer = LoginRequestSerializer(data=request_login)
    is_valid_login = login_serializer.is_valid()
    if not is_valid_login:
        raise SerializerError(login_serializer)

    # getting user and log in result message
    user_log = login_serializer.validated_data["user"]
    log_message = login_serializer.validated_data["log_message"]

    # converting user data back
    log_public_serializer = LoginResponseSerializer(user_log)
    public_log = dict(log_public_serializer.data)

    # results of work for all serializers
    result = {
        "1. UserCreateRequestSerializer: validation------": is_valid_create,
        "2. UserCreateResponseSerializer: user-----------": public_create,
        "3. LoginRequestSerializer: login result---------": log_message,
        "4. LoginResponseSerializer: logged user---------": public_log,
    }

    return HttpResponse(
        content_type="application/json",
        content=json.dumps(result),
    )
