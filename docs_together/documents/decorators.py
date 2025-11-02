from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from .models import Document


def owner_or_collaborator_required(function):
    def wrap(request, *args, **kwargs):
        document = get_object_or_404(Document, id=kwargs['document_id'])
        if request.user in document.collaborators.all() or request.user == document.owner:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def owner_required(function):
    def wrap(request, *args, **kwargs):
        document = get_object_or_404(Document, id=kwargs['document_id'])
        if document.owner == request.user:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
