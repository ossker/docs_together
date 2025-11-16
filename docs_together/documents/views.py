from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .decorators import owner_or_collaborator_required, owner_required
from .models import Document, DocumentInvitation, DocumentChangelog
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from diff_match_patch import diff_match_patch


@login_required
def view_documents(request):
    owned_documents = Document.objects.filter(owner=request.user)
    shared_documents = Document.objects.filter(
        collaborators=request.user
    ).exclude(owner=request.user).distinct()
    return render(request, 'documents/documents.html', {'owned_documents': owned_documents, 'shared_documents': shared_documents})


@login_required
@owner_or_collaborator_required
def view_document(request, document_id):
    document = Document.objects.get(pk=document_id)
    chat_history = document.chat_messages.select_related('user').all()
    return render(request, 'documents/document.html', {'document': document, 'chat_history': chat_history})


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
        new_title = request.POST.get("title", "")
        new_content = request.POST.get("content", "")
        document = Document.objects.get(id=document_id)

        if document.content == new_content and document.title == new_title:
            return JsonResponse({"status": "ok"})

        DocumentChangelog.objects.create(
            document=document,
            editor=request.user,
            title=new_title,
            content=new_content,
            date_edited=timezone.now()
        )

        document.title = new_title
        document.content = new_content
        document.date_edited = timezone.now()
        document.summary_pending = True
        document.save(update_fields=["content", "date_edited", "summary_pending"])

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "invalid method"}, status=405)


@login_required
@owner_required
def delete_document(request, document_id):
    if request.method == "POST":
        document = Document.objects.get(pk=document_id)
        document.delete()
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "invalid method"}, status=405)


@login_required
def create_document(request):
    document = Document.objects.create(
        title="Nowy dokument",
        content="",
        owner=request.user,
        date_created=timezone.now(),
        date_edited=timezone.now()
    )
    return redirect("documents:document", document.id)


@login_required
@owner_or_collaborator_required
def view_document_changelogs(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    changelogs = document.changelogs.order_by("-date_edited")
    return render(request, "documents/changelogs.html", {"document": document, "changelogs": changelogs})


@login_required
@owner_or_collaborator_required
def view_document_changelog(request, document_id, document_changelog_id):
    document = get_object_or_404(Document, id=document_id)
    changelog = get_object_or_404(document.changelogs, id=document_changelog_id)

    previous_changelog = (document.changelogs.filter(date_edited__lt=changelog.date_edited)
                          .order_by("-date_edited").first())

    difference = None
    if previous_changelog:
        dmp = diff_match_patch()
        diffs = dmp.diff_main(previous_changelog.content, changelog.content)
        dmp.diff_cleanupSemantic(diffs)
        difference = dmp.diff_prettyHtml(diffs)

    return render(request, "documents/changelog.html", {"changelog": changelog, "difference": difference})
