from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


def get_object(request, object_model, pk):
    user = request.user
    obj = get_object_or_404(object_model, id=pk)

    return user, obj


def check_exists(object_model, exists, msg, **kwargs):
    if exists:
        if object_model.objects.filter().exists():
            return Response(
                {'error': msg},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        if not object_model.objects.filter(**kwargs).exists():
            return Response(
                {'error': msg},
                status=status.HTTP_400_BAD_REQUEST
            )
