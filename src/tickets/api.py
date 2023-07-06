from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tickets.models import Message, Ticket
# fmt: off
from tickets.permissions import IsOwner, RoleIsAdmin, RoleIsManager, RoleIsUser
from tickets.serializers import (MessageSerializer, TicketSerializer,
                                 TicketTakeSerializer)
from users.constants import Role

# fmt: on

User = get_user_model()


class TicketAPIViewSet(ModelViewSet):
    serializer_class = TicketSerializer

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        all_tickets = Ticket.objects.all()

        if user.role == Role.ADMIN:
            return all_tickets
        elif user.role == Role.MANAGER:
            return all_tickets.filter(Q(manager=user) | Q(manager=None))
        else:
            # User's role fallback solution
            return all_tickets.filter(user=user)

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [RoleIsAdmin | RoleIsManager | RoleIsUser]
        elif self.action == "create":
            permission_classes = [RoleIsUser]
        elif self.action == "retrieve":
            permission_classes = [IsOwner | RoleIsAdmin | RoleIsManager]
        elif self.action == "update":
            permission_classes = [RoleIsAdmin | RoleIsManager]
        elif self.action == "destroy":
            permission_classes = [RoleIsAdmin | RoleIsManager]
        elif self.action == "take" or self.action == "reject":
            permission_classes = [RoleIsManager]
        elif self.action == "assign":
            permission_classes = [RoleIsAdmin]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["put"])
    def take(self, request, pk):
        ticket = self.get_object()

        # * ===== CUSTOM SERVISE APPROACH ===== *
        # updated_ticket = TakeServise(ticket).take_ticket(request.user)
        # serializer = self.get_serializer(updated_ticket)

        # * ===== SERIALIZER APPROACH ===== *
        serializer = TicketTakeSerializer(data={"manager_id": request.user.id})
        serializer.is_valid()

        ticket = serializer.take(ticket)

        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=["put"])
    def reject(self, request, pk):
        ticket = self.get_object()
        serializer = TicketTakeSerializer(data={"manager_id": request.user.id})
        serializer.is_valid()

        ticket = serializer.reject(ticket)

        return Response(TicketSerializer(ticket).data)

    @action(detail=True, methods=["put"])
    def assign(self, request, pk):
        ticket = self.get_object()
        serializer = TicketTakeSerializer(
            data={"manager_id": self.request.data["manager_id"]}
        )
        serializer.is_valid()

        ticket = serializer.assign(ticket)

        return Response(TicketSerializer(ticket).data)


class MessageListCreateAPIView(ListCreateAPIView):
    serializer_class = MessageSerializer
    lookup_field = "ticket_id"

    @staticmethod
    def get_ticket(user: User, ticket_id: int) -> QuerySet:
        """Get tickets for current user."""

        tickets = Ticket.objects.filter(Q(user=user) | Q(manager=user))
        return get_object_or_404(tickets, id=ticket_id)

    def get_queryset(self) -> QuerySet:
        ticket_id = self.kwargs[self.lookup_field]
        ticket = self.get_ticket(self.request.user, ticket_id)

        return Message.objects.filter(ticket=ticket)

    def post(self, request, ticket_id: int):
        ticket = self.get_ticket(request.user, ticket_id)
        payload = {
            "ticket": ticket.id,
            "text": request.data["text"],
            "user": request.user.id,
        }

        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
