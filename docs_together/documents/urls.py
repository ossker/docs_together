from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.documents_view, name='documents'),
    path('<document_id>', views.document_view, name='document'),
    path('<uuid:document_id>/invite/', views.generate_link, name='generate_link'),
    path('join/<uuid:token>/', views.join_document, name='join_document'),
]
