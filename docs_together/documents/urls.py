from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.documents_view, name='documents'),
    path('<document_id>', views.document_view, name='document')
]
