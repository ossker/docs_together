from django.urls import path
from . import views
from .ai import views as ai_views

app_name = 'documents'

urlpatterns = [
    path('', views.view_documents, name='documents'),
    path('<uuid:document_id>', views.view_document, name='document'),
    path("<uuid:document_id>/save", views.save_document, name='save_document'),
    path("<uuid:document_id>/delete", views.delete_document, name='delete_document'),
    path('<uuid:document_id>/invite/', views.generate_link, name='generate_link'),
    path('<uuid:document_id>/changelogs', views.view_document_changelogs, name='view_document_changelogs'),
    path('<uuid:document_id>/ai/summarize', ai_views.summarize, name='document_ai_summarize'),
    path('join/<uuid:token>/', views.join_document, name='join_document'),
    path('create', views.create_document, name='create_document'),
]
