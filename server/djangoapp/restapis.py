import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend and sentiment analyzer URLs from environment variables
backend_url = os.getenv('backend_url', default="http://localhost:3030")
sentiment_analyzer_url = os.getenv('sentiment_analyzer_url',
                                   default="http://localhost:5050/")


# Function to make GET requests
def get_request(endpoint, **kwargs):
    params = ""
    if kwargs:
        # Format parameters if provided
        params = "&".join([f"{key}={value}" for key, value in kwargs.items()])

    # Build the complete request URL
    if params:
      request_url = f"{backend_url}{endpoint}?{params}"
    else:
      request_url = f"{backend_url}{endpoint}"

    print(f"GET request to: {request_url}")
    try:
        # Perform GET request
        response = requests.get(request_url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error in GET request: {e}")
        return {"status": "Error", "message": str(e)}


# Function to analyze sentiment of review text
def analyze_review_sentiments(text):
    request_url = f"{sentiment_analyzer_url}analyze/{text}"
    try:
        # Perform GET request to sentiment analyzer API
        response = requests.get(request_url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Error in sentiment analysis request: {err}")
        return {"status": "Error", "message": str(err)}


# Function to post a review to the backend
def post_review(data_dict):
    request_url = f"{backend_url}/insert_review"
    print(f"Request URL: {request_url}")
    print(f"Data being sent: {data_dict}")

    try:
        # Perform POST request to insert review
        response = requests.post(request_url, json=data_dict)
        response.raise_for_status()  # Raise an error for bad status codes

        # Try to parse the response as JSON
        try:
            response_data = response.json()
            print(f"Response Data: {response_data}")
            return response_data
        except ValueError:
            # If the response isn't JSON, return the plain response
            print(f"Response is not JSON: {response.text}")
            return {"status": "error", "message": "Invalid JSON response",
                    "data": response.text}
    except requests.exceptions.RequestException as e:
        print(f"Error in POST request: {e}")
        return {"status": "error", "message": str(e)}
