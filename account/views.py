from django.contrib.auth.decorators import login_required
from .models import Team, Account
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from django.contrib.auth import authenticate, login, logout

from .forms import SignUpForm, LoginForm, TeamForm


@require_http_methods(["GET"])
def home(request):
    team = Account.objects.get(id=request.user.id)

    if team.team is None:
        context = {
            "team": None
        }
        return render(request, 'home.html', context)

    context = {
        'team': team.team.name
    }
    return render(request, 'home.html', context)


@require_http_methods(["GET", "POST"])
def signup(request):
    form = SignUpForm
    if request.method == "GET":
        context = {
            'form': form
        }
        return render(request, 'signup.html', context)
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            account = Account(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
            )
            account.save()
            login(request, account)
            return redirect('team')

        return redirect('signup')


@require_http_methods(["GET", "POST"])
def login_account(request):
    form = LoginForm
    if request.method == "GET":
        context = {
            'form': form
        }
        return render(request, 'login.html', context)
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")

        return redirect('login')


@require_http_methods(["GET"])
def logout_account(request):
    logout(request)
    return redirect('login')


@login_required
@require_http_methods(["GET", "POST"])
def joinoradd_team(request):
    if request.method == "GET":
        user = Account.objects.get(id=request.user.id)
        if user.team is not None:
            return redirect('home')
        if user.team is None:
            form = TeamForm
            context = {
                'form': form
            }

            return render(request, 'team.html', context)

    if request.method == "POST":
        form = TeamForm(request.POST)
        if form.is_valid():
            user = Account.objects.get(id=request.user.id)
            try:
                team = Team.objects.get(name__exact=form.cleaned_data.get('name'))
                print(team)
                user.team = team
                user.save()
                return redirect('home')
            except Team.DoesNotExist:
                new_team = Team(
                    name=form.cleaned_data.get('name'),
                    jitsi_url_path="http://meet.jit.si/" + form.cleaned_data.get('name')
                )
                new_team.save()
                user.team = new_team
                user.save()
                return redirect('home')
        return redirect('home')


@require_http_methods(["GET"])
def exit_team(request):
    user = Account.objects.get(id=request.user.id)
    if user.team is not None:
        user.team = None
        user.save()
        return redirect('home')
    if user.team is None:
        return redirect('home')
