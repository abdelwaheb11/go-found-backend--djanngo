from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer ,UserProfileSerializer , TopCreatorSerializer , TopInvestorSerializer
from rest_framework.authtoken.models import Token
from .models import UserProfile
from django.db.models import Count , Sum

class RegisterView(APIView):
    permission_classes = []
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
            try:
                user_profile = UserProfile.objects.get(user=user) 
                role = user_profile.role
            except UserProfile.DoesNotExist:
                return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

            return Response({"token": token.key , "role" : role }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):

    def post(self, request):
        logout(request)
        return Response({"message": "User logged out successfully!"}, status=status.HTTP_200_OK)
    

class UpdateUserProfileView(APIView):

    def put(self, request):
        try:
            # Récupérer le profil utilisateur
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"message": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

        # Mettre à jour les champs de l'utilisateur
        user = request.user
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.email = request.data.get('email', user.email)
        user.save()

        # Mettre à jour les champs du profil
        user_profile.desc = request.data.get('desc', user_profile.desc)

        # Si une image est envoyée, la sauvegarder
        if 'image' in request.FILES:
            user_profile.image = request.FILES['image']

        user_profile.save()

        # Retourner les données mises à jour
        return Response({
            "message": "Profile updated successfully",
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
            },
            "profile": {
                "desc": user_profile.desc,
                "image": user_profile.image.url if user_profile.image else None,
            },
        }, status=status.HTTP_200_OK)


    
class UserDetailView(APIView):
    def get(self, request, *args, **kwargs):
        user_profile = UserProfile.objects.get(user=request.user)  
        serializer = UserProfileSerializer(user_profile)  
        return Response(serializer.data)

class IsAuthenticated(APIView):

    def get(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)  
            serializer = UserProfileSerializer(user_profile)  
            return Response({"role": serializer.data["role"]}, status=200)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found"}, status=404)
        

class TopCreatorsAPIView(APIView):
    permission_classes = []  

    def get(self, request):
        creators = (
            UserProfile.objects.filter(role='creator', projects__isActive=True)
            .annotate(project_count=Count('projects'))
            .order_by('-project_count')[:10]
        )
        
        serializer = TopCreatorSerializer(creators, many=True)
        return Response(serializer.data)
    
class TopInvestorsAPIView(APIView):
    permission_classes = []
    def get(self, request):
        investors = (
            UserProfile.objects.filter(role='investor')
            .annotate(total_investment=Sum('investments__amount'))
            .order_by('-total_investment')[:10]
        )
        
        serializer = TopInvestorSerializer(investors, many=True)
        return Response(serializer.data)
    
class GetUserByUsername(APIView):
    def get(self, request,username):
        try:
            user_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = UserProfileSerializer(user_profile)

        return Response(serializer.data, status=status.HTTP_200_OK)