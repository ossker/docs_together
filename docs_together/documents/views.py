import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .decorators import owner_or_collaborator_required, owner_required
from .models import Document, DocumentInvitation, DocumentChangelog
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from diff_match_patch import diff_match_patch
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

User = get_user_model()

@login_required
def view_documents(request):

    def paginate(request, queryset, param_name='page', per_page=3):
        paginator = Paginator(queryset, per_page)
        page_number = request.GET.get(param_name)
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        return page_obj

    owned_list = Document.objects.filter(owner=request.user)
    shared_list = Document.objects.filter(collaborators=request.user).exclude(owner=request.user).distinct()

    owned_documents = paginate(request, owned_list, 'page')
    shared_documents = paginate(request, shared_list, 'page2')

    return render(
        request,
        'documents/documents.html',
        {
            'owned_documents': owned_documents,
            'shared_documents': shared_documents
        }
    )


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

    return redirect("documents:document", document_id=document.id)


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
        document.save(update_fields=["title", "content", "date_edited", "summary_pending"])

        return JsonResponse({"status": "ok"})

    return JsonResponse({"error": "invalid method"}, status=405)


@login_required
@owner_required
def delete_document(request, document_id):
    if request.method == "POST":
        document = Document.objects.get(pk=document_id)
        document.delete()
    return redirect('documents:documents')


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


def extract_content_from_pages(html_content):
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, "html.parser")
    pages = soup.find_all(class_="page")
    
    if pages:
        return "".join([page.decode_contents() for page in pages])
    
    return html_content

@login_required
@owner_or_collaborator_required
def view_document_changelog(request, document_id, document_changelog_id):
    document = get_object_or_404(Document, id=document_id)
    changelog = get_object_or_404(document.changelogs, id=document_changelog_id)

    previous_changelog = (document.changelogs.filter(date_edited__lt=changelog.date_edited)
                          .order_by("-date_edited").first())

    difference = None
    if previous_changelog:
        text1 = extract_content_from_pages(previous_changelog.content)
        text2 = extract_content_from_pages(changelog.content)

        dmp = diff_match_patch()
        
        diffs = dmp.diff_main(text1, text2)
        dmp.diff_cleanupSemantic(diffs)

        html_output = []
        for op, data in diffs:
            if op == dmp.DIFF_INSERT:
                html_output.append(f'<ins style="background:#e6ffe6;">{data}</ins>')
            elif op == dmp.DIFF_DELETE:
                html_output.append(f'<del style="background:#ffe6e6;">{data}</del>')
            elif op == dmp.DIFF_EQUAL:
                html_output.append(data)
        
        diff_html = "".join(html_output)

        difference = f'<div class="page" contenteditable="true">{diff_html}</div>'

    return render(request, "documents/changelog.html", {
        "changelog": changelog, 
        "difference": difference, 
        "document_id": document_id
    })


@login_required
@owner_or_collaborator_required
def export_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    html_content = render_to_string("documents/export_template.html", {"document": document})
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="{document.title}.html"'
    response.write(html_content)
    return response

@login_required
def import_document(request):
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        html_text = uploaded_file.read().decode("utf-8")
        title = os.path.splitext(uploaded_file.name)[0]
        soup = BeautifulSoup(html_text, "html.parser")
        body_content = soup.body.decode_contents() if soup.body else html_text

        document = Document.objects.create(
            title=title,
            content=body_content,
            owner=request.user,
            date_created=timezone.now(),
            date_edited=timezone.now()
        )
        return redirect("documents:document", document.id)
    return render(request, "documents/upload.html")


@login_required
@owner_required
def remove_collaborator(request, document_id, user_id):
    if request.method == "POST":
        document = get_object_or_404(Document, pk=document_id)
        user_to_remove = get_object_or_404(User, pk=user_id)

        if user_to_remove == document.owner:
            return JsonResponse({"error": "Nie możesz usunąć właściciela dokumentu"}, status=400)

        document.collaborators.remove(user_to_remove)
    return redirect('documents:documents')

@login_required
@owner_or_collaborator_required
def leave_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)

    if document.owner == request.user:
        return JsonResponse({"error": "Właściciel nie może opuścić własnego dokumentu."}, status=400)

    if request.method == "POST":
        document.collaborators.remove(request.user)
        return redirect("documents:documents")

    return JsonResponse({"error": "invalid method"}, status=405)