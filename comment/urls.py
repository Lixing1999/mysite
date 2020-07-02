from django.urls import path
from . import views

urlpatterns = [
    path('up_data_comment', views.up_data_comment, name='up_data_comment')
]