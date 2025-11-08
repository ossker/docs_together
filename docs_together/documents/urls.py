from django.urls import path
from . import views
from .ai import views as ai_views

app_name = 'documents'

urlpatterns = [
    path('', views.documents_view, name='documents'),
    path('<uuid:document_id>/invite/', views.generate_link, name='generate_link'),
    path('join/<uuid:token>/', views.join_document, name='join_document'),
    path('<uuid:document_id>/ai/summarize', ai_views.summarize, name='document_ai_summarize'),
    path("<uuid:document_id>/save", views.save_document, name="save_document"),
    path('<uuid:document_id>', views.document_view, name='document'),
]
