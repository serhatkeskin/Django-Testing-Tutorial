from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout



# Create your views here.
def home_view(request):
    template_path = 'myapp/home.html'
    return render(request, template_path)

def login_view(request):
    template_path = 'myapp/login.html'

    # If the request is POST, process the form
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            return render(request, template_path, {'error': 'Username and password are required.'})

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user:
            # Log the user in
            login(request, user)
            print("### User is authenticated: ", user.is_authenticated)
            return redirect('home')
        else:
            # Return error to template
            print("### User is not authenticated. Invalid username or password.")
            return render(request, template_path, {'error': 'Invalid username or password.'})

    # For GET requests, render the login page
    return render(request, template_path)

def logout_view(request):
    logout(request)
    print("### User is logged out.")
    return redirect('login')
