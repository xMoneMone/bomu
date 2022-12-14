from django.shortcuts import render, redirect
from userprofile.forms import CreateUserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from userprofile.models import UserProfile
from django.contrib.auth.models import User
from posts.models import CanvasPost
from django.views import View


class ShowProfile(View):
    def get(self, request, uname):
        if User.objects.filter(username=uname).exists():
            cur_profile = User.objects.get(username=uname)
            posts = CanvasPost.objects.filter(user=cur_profile).order_by('-id')
        else:
            return render(request, template_name="404.html")

        context = {"cur_profile": cur_profile,
                   "posts": posts}
        return render(request, template_name="profile.html", context=context)


def usersignup(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                user_profile = UserProfile(user=request.user)
                user_profile.save()
                return redirect('home')

    context = {"form": form}
    return render(request, template_name="signup.html", context=context)


def userlogin(request):
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(request.GET.get('next', 'home'))
            else:
                messages.info(request, "Wrong username or password.")
        else:
            messages.info(request, "Wrong username or password.")

    context = {"form": form}
    return render(request, template_name="login.html", context=context)


class UserLogout(View):
    def get(self, request):
        logout(request)
        return redirect('login')


@login_required(login_url='login')
def userdelete(request, uname):
    if not User.objects.filter(username=uname).exists():
        return render(request, template_name="404.html")
    user = User.objects.get(username=uname)
    if user != request.user and not request.user.is_superuser:
        return redirect('home')
    user.delete()
    return redirect('signup')


@login_required(login_url='login')
def useredit(request, uname):
    if not User.objects.filter(username=uname).exists():
        return redirect('home')
    cur_user = User.objects.get(username=uname)
    user_profile = UserProfile.objects.get(user=cur_user)
    if cur_user != request.user and not request.user.is_staff and not request.user.is_superuser:
        return redirect('home')
    if request.method == 'GET':
        form = UserProfileForm(instance=user_profile, initial=user_profile.__dict__)
    else:
        form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('show profile', str(cur_user))
        else:
            messages.info(request, ":(")

    context = {"profile_form": form,
               "cur_user": cur_user}
    return render(request, template_name="editprofile.html", context=context)
