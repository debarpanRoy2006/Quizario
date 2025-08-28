from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer

# Get the active User model
User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Handles user registration.
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"user": UserSerializer(user).data, "token": token.key}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Handles user login and returns an auth token.
    """
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"user": UserSerializer(user).data, "token": token.key})
    return Response({"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_user(request):
    """
    Handles user logout by deleting their auth token.
    Requires an authenticated user.
    """
    if request.auth:
        request.auth.delete()
        return Response({"success": "Logged out successfully"})
    return Response({"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)


class PasswordResetRequestAPI(APIView):
    """
    Starts the password reset process by sending an email to the user.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # IMPORTANT: Replace with your actual frontend URL
            reset_link = f"https://your-frontend-domain.com/reset-password/{uid}/{token}/"

            subject = "Password Reset for Your Quiz App Account"
            message = f"Hello,\n\nPlease click the link below to reset your password:\n{reset_link}\n\n"
            
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        except User.DoesNotExist:
            # Do not reveal that the user does not exist
            pass
        
        # Always return a generic success message to prevent user enumeration
        return Response({'message': 'If an account with that email exists, a password reset link has been sent.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPI(APIView):
    """
    Completes the password reset process.
    Expects uid, token, and the new password.
    """
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')

            if not new_password or not confirm_password:
                return Response({'error': 'Both new_password and confirm_password are required.'}, status=status.HTTP_400_BAD_REQUEST)

            if new_password != confirm_password:
                return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()
            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid reset link.'}, status=status.HTTP_400_BAD_REQUEST)
