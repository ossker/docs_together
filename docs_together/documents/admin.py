from django.contrib import admin
from .models import Document
from .models import DocumentInvitation
from .models import ChatMessage

admin.site.register(Document)
admin.site.register(DocumentInvitation)
admin.site.register(ChatMessage)