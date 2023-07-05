from django.contrib.auth import get_user_model

from tickets.models import Ticket

User = get_user_model()


# ===== FUNCTION IMPLEMENTATION =====
# def manager_takes(user: User, ticket: Ticket) -> Ticket:
#     if not ticket.manager:
#         ticket.manager = user
#         ticket.save()

#         return ticket


# ===== CLASS IMPLEMENTATION =====
class TakeServise:
    def __init__(self, ticket: Ticket):
        self._ticket = ticket

    def take_ticket(self, user: User):
        self._ticket.manager = user
        self._ticket.save()
