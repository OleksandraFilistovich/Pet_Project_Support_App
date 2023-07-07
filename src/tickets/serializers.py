from rest_framework import serializers

from tickets.models import Message, Ticket


class TicketSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Ticket
        fields = ["id", "manager", "user", "title", "status"]
        read_only_fields = ["visibility", "manager"]


class TicketTakeSerializer(serializers.Serializer):
    manager_id = serializers.IntegerField()

    def validate_manager_id(self, manager_id):
        # ? You can handle the specific validation if
        # ? the manager already has 10 tickets assigned
        return manager_id

    def take(self, ticket: Ticket) -> Ticket:
        if not ticket.manager_id:
            ticket.manager_id = self.validated_data["manager_id"]
            ticket.save()
        else:
            raise PermissionError

        return ticket

    def reject(self, ticket: Ticket) -> Ticket:
        if ticket.manager_id == self.validated_data["manager_id"]:
            ticket.manager_id = None
            ticket.save()
        else:
            raise PermissionError

        return ticket

    def assign(self, ticket: Ticket):
        if ticket.manager_id != self.validated_data["manager_id"]:
            ticket.manager_id = self.validated_data["manager_id"]
            ticket.save()
        else:
            raise ValueError(
                "Wrong ID. This manager already assigned to this ticket.",
            )

        return ticket


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "ticket", "text", "user", "timestamp"]
        read_only_fields = ["id", "timestamp"]

    def validate(self, attrs):
        return attrs
