from django.conf import settings
from django.db import models

from tickets.constants import TICKET_STATUS


class Ticket(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    visibility = models.BooleanField(default=True)
    status = models.PositiveSmallIntegerField(
        default=TICKET_STATUS.NOT_STARTED,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="user_tickets",
    )
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="managed_tickets",
        null=True,
    )

    class Meta:
        db_table = "tickets"


class Message(models.Model):
    text = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.RESTRICT,
        related_name="messages",
    )
    ticket = models.ForeignKey(
        "tickets.Ticket",
        on_delete=models.RESTRICT,
        related_name="messages",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"
