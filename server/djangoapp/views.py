from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from .restapis import get_request, analyze_review_sentiments, post_review
from .models import CarMake, CarModel
from .populate import initiate
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
@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, 
                                        first_name=first_name, last_name=last_name, 
                                        password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)


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
    # if dealer id has been provided
    if (dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def add_review(request):
    if (request.user.is_anonymous is False):
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception:
            return JsonResponse({"status": 401, "message":
                                 "Error in posting review"})
        finally:
            print("add_review request successful!")
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
