from django.urls import path
from . import views
from .ai import views as ai_views

app_name = 'documents'

urlpatterns = [
    path('', views.documents_view, name='documents'),
    path('<document_id>', views.document_view, name='document'),
    path('<document_id>/ai/summarize', ai_views.summarize, name='document_ai_summarize')
]
