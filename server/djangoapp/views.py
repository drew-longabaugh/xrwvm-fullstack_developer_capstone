from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
import logging
import json

# Initialize logger
logger = logging.getLogger(__name__)

# Login view
@csrf_protect
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('userName', '')
            password = data.get('password', '')

            # Authenticate user
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return JsonResponse({"status": "Authenticated", "userName": username})
            else:
                return JsonResponse({"status": "Error", "message": "Invalid credentials"}, status=401)
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"status": "Error", "message": "Invalid request data"}, status=400)
    return JsonResponse({"status": "Error", "message": "Only POST method allowed"}, status=405)

# Logout view
def logout_request(request):
    logout(request)
    data = {"userName":""}
    return JsonResponse(data)
    #logout(request)
    #return JsonResponse({"status": "Logged out"})

# Registration view
@csrf_protect
def registration(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get('userName', '')
            password = data.get('password', '')
            first_name = data.get('firstName', '')
            last_name = data.get('lastName', '')
            email = data.get('email', '')

            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({"status": "Error", "message": "Username already exists"}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({"status": "Error", "message": "Email already registered"}, status=400)

            # Create user
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
            login(request, user)
            return JsonResponse({"status": "Authenticated", "userName": username})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"status": "Error", "message": "Invalid request data"}, status=400)
    return JsonResponse({"status": "Error", "message": "Only POST method allowed"}, status=405)
