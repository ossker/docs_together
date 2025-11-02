import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=256)
    content = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_documents', on_delete=models.CASCADE)
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_documents')
    date_created = models.DateTimeField(default=timezone.now)
    date_edited = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'"{self.title}" by {self.owner}'
