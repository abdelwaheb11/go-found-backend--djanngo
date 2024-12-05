from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer ,UserProfileSerializer
from rest_framework.authtoken.models import Token
from .models import UserProfile

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = []
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = User.objects.filter(username=username).first()

        if user and user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            login(request, user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):

    def post(self, request):
        logout(request)
        return Response({"message": "User logged out successfully!"}, status=status.HTTP_200_OK)
    

class UpdateUserProfileView(APIView):
    def put(self, request):
        try:
            # Récupérer le profil utilisateur actuel
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"message": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Assurez-vous que le champ 'username' est retiré des données reçues
        request_data = request.data.copy()
        if 'user' in request_data and 'username' in request_data['user']:
            del request_data['user']['username']

        # Sérialisation des données de la requête
        serializer = UserProfileSerializer(user_profile, data=request_data, partial=True)

        if serializer.is_valid():
            # Sauvegarder les données mises à jour
            serializer.save()
            return Response({"message": "User profile updated successfully!"}, status=status.HTTP_200_OK)

        # Retourner les erreurs si elles existent
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class UserDetailView(APIView):
    def get(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(user=request.user)  
        serializer = UserProfileSerializer(user_profile)  
        return Response(serializer.data)