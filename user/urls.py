from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.userlogin, name='userlogin'),
    path('register/', views.register, name='register'),
    path('login_for_modal/', views.login_for_modal, name='login_for_modal'),
    path('logout/', views.userlogout, name='userlogout'),
    path('user_info/', views.user_info, name='user_info'),
    path('change_nickname/', views.change_nickname, name='change_nickname'),
    path('bind_email/', views.bind_email, name='bind_email'),
    path('send_varification_code/', views.send_varification_code, name='send_varification_code'),
    path('change_password/', views.change_password, name='change_password'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
]