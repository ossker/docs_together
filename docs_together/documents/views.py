from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .decorators import owner_or_collaborator_required, owner_required
from .models import Document, DocumentInvitation
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import PermissionDenied

@login_required
def documents_view(request):
    owned_documents = Document.objects.filter(owner=request.user)
    shared_documents = Document.objects.filter(
        collaborators=request.user
    ).exclude(owner=request.user).distinct()
    return render(request, 'documents/documents.html', {'owned_documents': owned_documents,'shared_documents': shared_documents})


@login_required
@owner_or_collaborator_required
def document_view(request, document_id):
    document = Document.objects.get(pk=document_id)
    chat_history = document.chat_messages.select_related('user').all()
    return render(request, 'documents/document.html', {'document': document, 'chat_history': chat_history,})


@login_required
@owner_required
def generate_link(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    invite = DocumentInvitation.objects.create(
        document=document,
        created_by=request.user,
    )

    link = request.build_absolute_uri(f"/documents/join/{invite.token}/")
    return JsonResponse({"invite_link": link})


@login_required
def join_document(request, token):
    invitation = get_object_or_404(DocumentInvitation, token=token)

    if not invitation.is_valid():
        return render(request, "documents/invite_invalid.html", {"invitation": invitation})

    document = invitation.document
    document.collaborators.add(request.user)
    invitation.used = True
    invitation.save()

    return redirect("documents:document", doc_id=document.id)


@csrf_exempt
@login_required
@owner_or_collaborator_required
def save_document(request, document_id):
    if request.method == "POST":
        document = Document.objects.get(id=document_id)
        document.content = request.POST.get("content", "")
        document.date_edited = timezone.now()
        document.summary_pending = True
        document.save(update_fields=["content", "date_edited", "summary_pending"])
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "invalid method"}, status=405)
