from django.urls import path

from admin_app import views as vws

app_name = 'admin_app'

# Публичное API
urlpatterns = [
    path('load/', vws.PostAPIView.as_view(), name='post_view'),
]
