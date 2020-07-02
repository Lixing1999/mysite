import random
import string
import time

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import BindEmailForm, ChangeNicknameForm, LoginForm, RegForm, ChangePasswordForm, ForgotPasswordForm
from .models import Profile


def userlogin(request):

    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']   
            login(request, user) 
            return redirect(request.GET.get('from', reverse('home')))

    else:
        login_form = LoginForm()

    context = {}
    context['login_form'] = login_form
    return render(request, 'user/login.html', context)    

def login_for_modal(request):
    login_form = LoginForm(request.POST)
    data = {}
    if login_form.is_valid():
        user = login_form.cleaned_data['user']   
        login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)
        

def register(request):
    if request.method == 'POST':
        register_form = RegForm(request.POST, request=request)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            email = register_form.cleaned_data['email']
            password = register_form.cleaned_data['password']

            # 创建用户
            user = User.objects.create_user(username, email, password)
            user.save()
            '''
            等同于上面的创建用户
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            user.save()
            '''
            # 清楚用过的验证码（服务器缓存session）
            del request.session['register_code']
            # 登录用户
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:
        register_form = RegForm()

    context = {}
    context['register_form'] = register_form
    return render(request, 'user/register.html', context)


def userlogout(request):
    logout(request)
    return redirect(request.GET.get('from', reverse('home')))


def user_info(request):
    context = {}
    return render(request, 'user/user_info.html', context)


def change_nickname(request):
    redirect_to = request.GET.get('form', reverse('home'))

    if request.method == 'POST':
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():
            nickname_new = form.cleaned_data['new_nickname']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '确认'
    context['form'] = form
    context['return_back_url'] = redirect_to
    return render(request, 'form.html', context)


def bind_email(request):
    redirect_to = request.GET.get('form', reverse('home'))
    if request.method == 'POST':
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清楚用过的验证码（服务器缓存session）
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '确认'
    context['form'] = form
    context['return_back_to'] = redirect_to
    return render(request, 'user/bind_email.html', context)    


# 发送邮箱验证码
def send_varification_code(request):
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    data = {}
    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 5))

        request.session['bind_email_code'] = code
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            request.session[send_for] = code
            request.session['send_code_time'] = now
            #发送验证码
            send_mail(
                '汪力行的博客',
                '验证码：%s' % code,
                '1170931378@qq.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


# 修改密码
def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            logout(request)
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '确认'
    context['form'] = form
    context['redirect_to'] = redirect_to

    return render(request, 'form.html', context)


def forgot_password(request):
    redirect_to = reverse('login')
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            # 清楚用过的验证码（服务器缓存session）
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '忘记密码'
    context['form_title'] = '忘记密码'
    context['submit_text'] = '确认修改' 
    context['form'] = form
    context['return_back_to'] = redirect_to
    return render(request, 'user/forgot_password.html', context)