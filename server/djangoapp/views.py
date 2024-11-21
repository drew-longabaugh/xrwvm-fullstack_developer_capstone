from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect
from .restapis import get_request, analyze_review_sentiments, post_review
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

#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})
