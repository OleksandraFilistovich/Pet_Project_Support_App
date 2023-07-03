from rest_framework import serializers

from tickets.models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Ticket
        fields = ["id", "manager", "title", "text", "status", "user"]
        read_only_fields = ["visibility", "manager"]


class TicketTakeSerializer(serializers.Serializer):
    manager_id = serializers.IntegerField()

    def validate_manager_id(self, manager_id):
        # ? You can handle the specific validation if
        # ? the manager already has 10 tickets assigned
        return manager_id
    
    def assign(self, ticket: Ticket) -> Ticket:
        if not ticket.manager_id:
            ticket.manager_id = self.validated_data["manager_id"]
            ticket.save()
        else:
            raise PermissionError

        return ticket
