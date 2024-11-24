from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect
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
                return JsonResponse({"status": "Error", "message": "Missing 'userName' or 'password'"}, status=400)

            # Authenticate user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"userName": username,
                                     "status": "Authenticated"})
            else:
                return JsonResponse({"status": "Error", "message":
                                     "Invalid username or password"}, status=401)
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
            logger.error(f"Unexpected error in registration: {e}")
            return JsonResponse({"status": "Error",
                                 "message": "Internal server error"}, status=500)
    return JsonResponse({"status": "Error", "message":
                         "Only POST method allowed"}, status=405)
