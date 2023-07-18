from django.db import models
from django.utils import timezone
from users.models import Client
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    message_text = models.TextField(max_length=255)
    filer = models.JSONField()


class Message(models.Model):
    class StarusChoise(models.TextChoices):
        CREATED = "CREATED", _("Created")
        PROCESSING = "PROCESSING", _("Processing")
        COMPLETE = "COMPLETE", _("Complete")
        ERROR = "ERROR", _("Error")

    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20,
                              choices=StarusChoise.choices,
                              default=StarusChoise.CREATED)
    dispatch = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='messages')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
