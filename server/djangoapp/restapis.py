# Uncomment the imports below before you add the function code
import requests
import os
from dotenv import load_dotenv
from django.http import JsonResponse
import json

load_dotenv()

backend_url = os.getenv(
    'backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    'sentiment_analyzer_url',
    default="http://localhost:5050/")


def get_request(endpoint, **kwargs):
    params = ""
    if(kwargs):
        for key, value in kwargs.items():
            params = params+key+"="+value+"&"

    request_url = backend_url+endpoint+"?"+params

    print("GET from {} ".format(request_url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except Exception as e:
        print(f"Error: {e}")


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url+"analyze/"+text
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(request_url)
        return response.json()
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")


def add_review(request):
    if request.method == "POST":  # Assuming POST method is required for adding reviews
        try:
            data = json.loads(request.body)
            response = post_review(data)  # Call your function to handle posting the review
            return JsonResponse({"status": 200, "message": 
                                 "Review added successfully"})
        except json.JSONDecodeError:  # Handle JSON parsing errors
            return JsonResponse({"status": 400, "message": 
                                 "Invalid JSON format"})
        except Exception as e:  # Catch other unexpected errors
            print(f"Error: {e}")
            return JsonResponse({"status": 401, "message": 
                                 "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
