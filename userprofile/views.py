from django.shortcuts import render, redirect
from userprofile.forms import CreateUserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from userprofile.models import UserProfile
from django.contrib.auth.models import User


@login_required(login_url='login')
def show_profile(request, uname):
    try:
        cur_profile = User.objects.get(username=uname)
    except:
        cur_profile = None

    context = {"cur_profile": cur_profile}
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
                return redirect('home')
            else:
                messages.info(request, "Wrong username or password.")
        else:
            messages.info(request, "Wrong username or password.")

    context = {"form": form}
    return render(request, template_name="login.html", context=context)


@login_required(login_url='login')
def userlogout(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def userdelete(request):
    user = request.user
    user.delete()
    return redirect('signup')


@login_required(login_url='login')
def useredit(request):
    user_profile = request.user.userprofile
    if request.method == 'GET':
        form = UserProfileForm(instance=user_profile, initial=user_profile.__dict__)
    else:
        form = UserProfileForm(request.POST or None, request.FILES or None, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            messages.info(request, ":(")

    context = {"profile_form": form}
    return render(request, template_name="editprofile.html", context=context)