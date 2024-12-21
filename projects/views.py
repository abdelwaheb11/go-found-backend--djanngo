from rest_framework.views import APIView
from .models import Project, Investment, Commentary , Image , Favorate
from .serializers import ProjectSerializer, InvestmentSerializer, CommentarySerializer , ImageSerializer , FavoriteSerializer
from rest_framework.response import Response
from rest_framework import status
from users.models import UserProfile
import os
from django.conf import settings
from django.db.models import Q
from users.serializers import UserProfileSerializer
from decimal import Decimal

class ProjectView(APIView):
    serializer_class = ProjectSerializer
    permission_classes = []
    def get(self, request , pk=None):
        if pk is None:
            category = request.GET.get('category')
            search = request.GET.get('search')
            if category :
                 queryset = Project.objects.filter(category=category)
            else :
                queryset = Project.objects.all()
            if search:
                search = search.strip().lower()
                queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
            serializer = self.serializer_class(queryset, many=True)
            data = serializer.data
            for item in data:
                item['images'] = Image.objects.filter(project_id=item['id']).values()

            return Response(data, status=status.HTTP_200_OK)
        else: 
            try:
                project = Project.objects.get(pk=pk)
            except Project.DoesNotExist:
                return Response({'detail': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.serializer_class(project)
            data = serializer.data
            creator_serializer = UserProfileSerializer(project.creator)
            data['creator'] = creator_serializer.data
            comment_serializer = CommentarySerializer(Commentary.objects.filter(project_id=pk),many = True)
            data['commentary'] = comment_serializer.data
            investment_Serializer = InvestmentSerializer(Investment.objects.filter(project_id=pk) , many = True)
            data['investment'] = investment_Serializer.data
            data['images'] = Image.objects.filter(project_id=pk).values()

            return Response(data, status=status.HTTP_200_OK)
    
    # Fonction POST pour créer un nouveau projet
    def post(self, request):
        try:
            # Vérifier si l'utilisateur est un créateur
            user_profile = UserProfile.objects.get(user=request.user, role='creator')  
        except UserProfile.DoesNotExist:
            return Response({'detail': 'User is not a creator.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        serializer = ProjectSerializer(data=data)

        if serializer.is_valid():
            project = serializer.save(creator=user_profile)
            if 'images' in request.FILES:
                images = request.FILES.getlist('images')
                for image_file in images:
                    try:
                        Image.objects.create(project=project, image=image_file)
                    except Exception as e:
                        return Response({'detail': f'Error saving image: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Fonction PUT pour mettre à jour un projet existant
    def put(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(project, data=request.data)
        if serializer.is_valid():
            serializer.save()  # Mettre à jour l'instance du projet
            if 'images' in request.FILES:
                images = request.FILES.getlist('images')
                for image_file in images:
                    Image.objects.create(project=project, image=image_file)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Fonction DELETE pour supprimer un projet
    def delete(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'detail': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        
        images = Image.objects.filter(project_id=pk)
        for image in images:
            if image.image:
                file_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
                if os.path.isfile(file_path):  
                    os.remove(file_path)

        project.delete()  # Supprimer le projet
        return Response(status=status.HTTP_204_NO_CONTENT)




# ViewSet pour Investment
class InvestmentView(APIView):
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

    def post(self, request, *args, **kwargs):
        serializer = InvestmentSerializer(data=request.data)   
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found for this user."}, status=status.HTTP_400_BAD_REQUEST)
        
        project_id = request.data.get('project')
        if not project_id:
            return Response({"error": "Project ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            amount = request.data.get('amount')
            try:
                amount = Decimal( amount)  
            except (ValueError, TypeError):
                return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(investor=user_profile, project=project)
            project.raised_amount += amount
            project.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        investments = Investment.objects.filter(investor=user_profile)
        serializer = InvestmentSerializer(investments, many=True)
        # Retourner les données sérialisées
        return Response(serializer.data, status=status.HTTP_200_OK)



# ViewSet pour Commentary
class CommentaryView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = CommentarySerializer(data=request.data)
        try:
            # Récupérer l'instance unique de UserProfile
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found for this user."}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            # Assigner l'instance UserProfile au commentaire
            serializer.save(user=user_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageView(APIView):
    serializer_class = ImageSerializer

    def delete(self, request, pk):
        try:
            image = Image.objects.get(pk=pk)
        except Image.DoesNotExist:
            return Response({"error": "Image not found"}, status=status.HTTP_400_BAD_REQUEST)

        file_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
        if os.path.isfile(file_path):
            os.remove(file_path)  

        image.delete() 

        return Response(status=status.HTTP_204_NO_CONTENT)


class SuggestionAPIView(APIView):
    permission_classes = []  # Public endpoint

    def get(self, request):
        query = request.GET.get('q', '').strip()

        if query:
            # Fetch project suggestions
            projects = (
                Project.objects.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(category__icontains=query)
                )
                .distinct()
                .values('id', 'title', 'category')[:5]
            )
            projects = list(projects)

            for project in projects:
                image_obj = Image.objects.filter(project_id=project['id']).first()
                project['image'] = image_obj.image.url if image_obj and image_obj.image else None

            # Fetch user profile suggestions
            users = list(
                UserProfile.objects.filter(
                    Q(user__first_name__icontains=query) |
                    Q(user__last_name__icontains=query) |
                    Q(desc__icontains=query)
                )
                .distinct()
                .values('id', 'user__first_name', 'user__last_name','user__username', 'image' , 'role')[:5]
            )

            # Combine results
            response_data = {
                "projects": projects,
                "users": users,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({"message": "No query provided", "projects": [], "users": []}, status=status.HTTP_200_OK)


class UserProjectsView(APIView):
    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found for this user."}, status=status.HTTP_400_BAD_REQUEST)
        projects = Project.objects.filter(creator=user_profile)

        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProjectUserByUsername(APIView):
    def get(self, request,username):
        try:
            user_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found."}, status=status.HTTP_400_BAD_REQUEST)
        projects = Project.objects.filter(creator=user_profile)

        serializer = ProjectSerializer(projects, many=True)
        data = serializer.data
        for item in data:
            item['images'] = Image.objects.filter(project_id=item['id']).values()

        return Response(data, status=status.HTTP_200_OK)
    
class InsetistementUserByUsername(APIView):
    def get(self, request,username):
        try:
            user_profile = UserProfile.objects.get(user__username=username)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found."}, status=status.HTTP_400_BAD_REQUEST)
        

        investments = Investment.objects.filter(investor=user_profile)
        serializer = InvestmentSerializer(investments, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class FavorateView(APIView):
    # Ajouter un favori
    def post(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found for this user."}, status=status.HTTP_400_BAD_REQUEST)

        project_id = kwargs.get('projectId')
        if not project_id:
            return Response({"error": "Project ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier si ce projet est déjà un favori pour cet utilisateur
        if Favorate.objects.filter(user=user_profile, project=project).exists():
            return Response({"error": "This project is already in favorites."}, status=status.HTTP_400_BAD_REQUEST)

        # Ajouter aux favoris
        Favorate.objects.create(user=user_profile, project=project)
        return Response({"message": "Project added to favorites successfully."}, status=status.HTTP_201_CREATED)

    # Supprimer un favori
    def delete(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found for this user."}, status=status.HTTP_400_BAD_REQUEST)

        project_id = kwargs.get('projectId')
        if not project_id:
            return Response({"error": "Project ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Vérifier et supprimer le favori
        favorate = Favorate.objects.filter(user=user_profile, project=project).first()
        if not favorate:
            return Response({"error": "Favorite not found for this project."}, status=status.HTTP_400_BAD_REQUEST)

        favorate.delete()
        return Response({"message": "Favorite removed successfully."}, status=status.HTTP_200_OK)

    # Obtenir tous les projets favoris de l'utilisateur connecté
    def get(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile not found for this user."}, status=status.HTTP_400_BAD_REQUEST)
        
        action = request.GET.get('action')
        if action:
            project_id = kwargs.get('projectId')
            if not project_id:
                return Response({"error": "Project ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                project = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                return Response({"error": "Project not found."}, status=status.HTTP_400_BAD_REQUEST)
            if action == 'count':
                count = Favorate.objects.filter(project=project).count()
                return Response({"favoriteCount": count}, status=status.HTTP_200_OK)
            elif action == 'isFavorited':
                is_favorited = Favorate.objects.filter(user=user_profile, project=project).exists()
                return Response({"isFavorited": is_favorited}, status=status.HTTP_200_OK)

        favorites = Favorate.objects.filter(user=user_profile).select_related('project')
        projects = [favorite.project for favorite in favorites]
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    

