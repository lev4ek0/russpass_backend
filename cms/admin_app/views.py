import os
from django.db.models import QuerySet, Prefetch
from rest_framework.generics import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.core.files import File

from admin_app.models import Photo
from triton_inference import TritonClient


class PostAPIView(generics.CreateAPIView):
    """
        APIView для заполнения базы фотками
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        directory = '/cms/photos'  # Укажите путь к директории с фотографиями
        
        for filename in os.listdir(directory):
            with open(os.path.join(directory, filename), 'rb') as file:
                client = TritonClient('tritonserver:8000', '/cms/bpe.model')

                res = client.inference_image(os.path.join(directory, filename))
                photo = Photo(embeding=res.tolist())
                photo.image.save(filename, File(file))
                photo.save()

        
        return "ok"
