from django.urls import path

from admin_app import views as vws

app_name = 'survey_app'

# Публичное API
endpoints = [
    path('load/', vws.StartSurveyAPIView.as_view(), name='start_survey'),
]
