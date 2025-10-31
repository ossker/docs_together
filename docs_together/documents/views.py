from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


# @login_required
def document(request):
    try:
        document = ...
    except:
        return HttpResponseForbidden()

    return render(request, 'documents/document.html')