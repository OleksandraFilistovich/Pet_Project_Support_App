from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.serializers import UserCreateSerializer, UserPublicSerializer


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        public_serializer = UserPublicSerializer(serializer.instance)
        headers = self.get_success_headers(public_serializer.data)
        return Response(
            public_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
