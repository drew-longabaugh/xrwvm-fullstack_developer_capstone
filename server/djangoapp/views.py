from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth import authenticate, login
from .restapis import get_request, analyze_review_sentiments, post_review
import logging
import json

# Initialize logger
logger = logging.getLogger(__name__)


# Login view
@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            # Parse JSON body
            data = json.loads(request.body)
            username = data.get('userName')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({"status": "Error",
                                     "message":
                                     "Missing 'userName' or 'password'"},
                                    status=400)

            # Authenticate user
            user = authenticate(username=username,
                                password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"userName": username,
                                     "status": "Authenticated"})
            else:
                return JsonResponse({"status": "Error",
                                     "message":
                                     "Invalid username or password"},
                                    status=401)
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in login_user")
            return JsonResponse({"status": "Error", "message":
                                 "Invalid JSON format"}, status=400)
    return JsonResponse({"status": "Error", "message":
                         "Only POST method allowed"}, status=405)


# Registration view
@csrf_protect
def registration(request):
    if request.method == "POST":
        try:
            # Parse JSON body
            data = json.loads(request.body)
            username = data.get('userName')
            password = data.get('password')
            first_name = data.get('firstName', '')
            last_name = data.get('lastName', '')
            email = data.get('email')

            # Check for missing fields
            if not username or not password or not email:
                return JsonResponse({"status": "Error", "message":
                                     "Missing required fields"}, status=400)

            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                return JsonResponse({"status": "Error", "message":
                                     "Username already exists"}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({"status": "Error", "message":
                                     "Email already registered"}, status=400)

            # Create user
            user = User.objects.create_user(username=username,
                                            password=password,
                                            first_name=first_name,
                                            last_name=last_name,
                                            email=email)
            login(request, user)
            return JsonResponse({"status": "Authenticated",
                                 "userName": username})
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in registration")
            return JsonResponse({"status": "Error", "message":
                                 "Invalid JSON format"}, status=400)
        except Exception as e:
            error_message = f"Unexpected error in registration: {e}"
            logger.error(error_message)
            return JsonResponse({"status":
                                 "Error", "message":
                                 "Internal server error"}, status=500)
    return JsonResponse({"status": "Error", "message":
                         "Only POST method allowed"}, status=405)



def logout_request(request):
    """Handle user logout."""
    logout(request)
    return JsonResponse({"userName": ""})
    
    
def get_cars(request):
    """Fetch car models and makes."""
    count = CarMake.objects.filter().count()

    if count == 0:
        initiate()

    car_models = CarModel.objects.select_related('car_make')
    cars = [
        {
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        }
        for car_model in car_models
    ]

    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    """Fetch dealerships."""
    endpoint = (
        f"/fetchDealers/{state}" if state != "All" else "/fetchDealers"
    )

    dealerships = get_request(endpoint)
    logger.debug(f"Dealerships data received: {dealerships}")

    if not dealerships:
        logger.error("No dealerships found or data fetch error.")

    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id):
    """Fetch dealer details by ID."""
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_reviews(request, dealer_id):
    """Fetch reviews of a dealer."""
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)

        for review in reviews:
            sentiment = analyze_review_sentiments(review['review'])
            review['sentiment'] = sentiment['sentiment']

        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def post_review(data_dict):
    request_url = backend_url+"/insert_review"
    try:
        response = requests.post(request_url,json=data_dict)
        print(response.json())
        return response.json()
    except:
        print("Network exception occurred")

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
