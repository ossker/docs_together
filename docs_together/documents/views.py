from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .decorators import owner_or_collaborator_required
from .models import Document


@login_required
def documents_view(request):
    documents = Document.objects.filter(Q(owner=request.user) | Q(collaborators=request.user)).distinct()
    return render(request, 'documents/documents.html', {'documents': documents})


@login_required
@owner_or_collaborator_required
def document_view(request, document_id):
    document = Document.objects.get(pk=document_id)
    return render(request, 'documents/document.html', {'document': document})
