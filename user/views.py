from rest_framework.generics import GenericAPIView
from rest_framework import generics, status, views, permissions
from .serializers import UserSerializer, LoginSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib import auth
import random
import redis
import logging
import jwt
from .models import User
from django.conf import settings
from .models import UserOTP
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError

redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)
logger = logging.getLogger('django')


# Create your views here.
class RegisterView(GenericAPIView):
    """
               This api is for registration of new user
              @param request: username,email and password
              @return: it will return the registered user with its credentials
    """
    serializer_class = UserSerializer

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user_data = serializer.data
            user = User.objects.get(email=user_data['email'])
            user.is_active = False
            user_otp = random.randint(100000, 999999)
            mess = f"Hello {user.username},\nYour OTP is {user_otp}\nThanks!"
            send_mail(
                "Welcome to Book Store Application - Verify Your Email",
                mess,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )
            redis_instance.set(user_otp, user.id)
            logger.info("User is Created and OTP is sent to user")
            return Response({"Message": "OTP Sent to the user "}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.exception(e,exc_info=True)
            return Response({"Error": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.exception(e,exc_info=True)
            return Response({"Error": "Something Went Wrong"}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(views.APIView):
    """
            This api is for verification OTP to this application
           @param request: once the account verification link is clicked by user this will take that request
           @return: it will return the response of OTP activation
     """

    def get(self, request):
        otp = request.data.get('otp')
        print(otp)
        try:
            value = redis_instance.get(otp)
            if not value:
                return Response("Invalid OTP", status=status.HTTP_400_BAD_REQUEST)
            else:
                user = User.objects.get(id=value)
                if not user.is_active:
                    user.is_active = True
                    user.save()
                redis_instance.delete(otp)
                return Response({'Message': "Successully Verified OTP"})

        except Exception as e:
            logger.error(e)
            return Response({'error': 'Something Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            data = request.data
            username = data.get('username', '')
            password = data.get('password', '')
            user = User.objects.get(username=username, password=password)
            # user = auth.authenticate(username=username, password=password)

            if user:
                auth_token = jwt.encode(
                    {'username': user.username}, settings.SECRET_KEY, algorithm='HS256')

                #serializer = UserSerializer(user)

                # data = {'user': serializer.data, 'token': auth_token}

                response = Response(
                    {'response': f'You are logged in successfully', 'username': username, 'token': auth_token},
                    status=status.HTTP_200_OK)
                response['Authorization'] = auth_token
                return response

            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(e)
            return Response({'error': 'Something Went Wrong'}, status=status.HTTP_400_BAD_REQUEST)
