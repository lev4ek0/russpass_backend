import os
from django.db.models import QuerySet, Prefetch
from rest_framework.generics import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from django.core.files import File

from admin_app.models import Photo
from cms.triton_inference import TritonClient


class PostAPIView(generics.CreateAPIView):
    """
        APIView для заполнения базы фотками
    """
    def post(self, request, *args, **kwargs):
        directory = '/app/photos'  # Укажите путь к директории с фотографиями
        
        for filename in os.listdir(directory):
            if filename.endswith(".jpg") or filename.endswith(".png"):  # Фильтруем файлы по расширениям
                with open(os.path.join(directory, filename), 'rb') as file:
                    photo = Photo()
                    client = TritonClient('tritonserver:8000', '/app/bpe.model')

                    res = client.inference_image(os.path.join(directory, filename))
                    photo.image.save(filename, File(file))
                    
                    photo.embeding = res
                    photo.save()
        
        return self.create(request, *args, **kwargs)
