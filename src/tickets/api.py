from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from tickets.models import Ticket
from tickets.permissions import IsOwner, RoleIsAdmin, RoleIsManager, RoleIsUser
from tickets.serializers import TicketSerializer, TicketTakeSerializer


class TicketAPIViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

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
        elif self.action == "take":
            permission_classes = [RoleIsManager]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=["post"])
    def take(self, request, pk):
        ticket = self.get_object()

        # ===== CUSTOM SERVISE APPROACH =====
        # updated_ticket = TakeServise(ticket).take_ticket(request.user)
        # serializer = self.get_serializer(updated_ticket)

        # ===== SERIALIZER APPROACH =====
        serializer = TicketTakeSerializer(data={"manager_id": request.user.id})
        serializer.is_valid()
        ticket = serializer.assign(ticket)

        return Response(TicketSerializer(ticket).data)
