from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


def get_object(request, object_model, pk):
    user = request.user
    obj = get_object_or_404(object_model, id=pk)

    return user, obj


def check_exists_and_create_or_delete(object_model, exists, msg, **kwargs):
    if exists:
        if object_model.objects.filter(**kwargs).exists():
            raise ValidationError(
                {'error': msg}
            )
        return object_model.objects.create(**kwargs)
    else:
        if not object_model.objects.filter(**kwargs).exists():
            raise ValidationError(
                {'error': msg},
            )
        object_model.objects.filter(**kwargs).delete()
