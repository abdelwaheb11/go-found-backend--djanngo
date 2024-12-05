from rest_framework.views import APIView
from .models import Project, Investment, Commentary , Image
from .serializers import ProjectSerializer, InvestmentSerializer, CommentarySerializer , ImageSerializer
from rest_framework.response import Response
from rest_framework import status
from users.models import UserProfile
import os
from django.conf import settings
from django.db.models import Q
from users.serializers import UserProfileSerializer


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
            data['investment'] = Investment.objects.filter(project_id=pk).values()
            data['image'] = Image.objects.filter(project_id=pk).values()

            return Response(data, status=status.HTTP_200_OK)
    
    # Fonction POST pour créer un nouveau projet
    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user, role='creator')  
        except UserProfile.DoesNotExist:
            return Response({'detail': 'User is not a creator.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        serializer = ProjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save(creator=user_profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
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
    

    def perform_create(self, serializer):
        serializer.save(investor=self.request.user.userprofile)  # L'utilisateur actuel est l'investisseur

# ViewSet pour Commentary
class CommentaryView(APIView):
    queryset = Commentary.objects.all()
    serializer_class = CommentarySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.userprofile)

class ImageView(APIView):
    serializer_class = ImageSerializer
    def delete(self, request, pk):
        image = Image.objects.filter(pk=pk).first()
        file_path = os.path.join(settings.MEDIA_ROOT, image.image.name)
        if os.path.isfile(file_path):  
            os.remove(file_path)
        image.delete()


class SuggestionAPIView(APIView):
    permission_classes = []  
    def get(self, request):
        query = request.GET.get('q', '').strip()

        if query:
            suggestions = (
                Project.objects.filter(
                    Q(title__icontains=query) |
                    Q(description__icontains=query) |
                    Q(category__icontains=query)
                )
                .distinct() 
                .values('id', 'title', 'category')[:10]  
            )
            for item in suggestions:
                image_obj = Image.objects.filter(project_id=item['id']).first()
                item['image'] = image_obj.image.url if image_obj and image_obj.image else None

            return Response(list(suggestions), status=status.HTTP_200_OK)

        return Response([], status=status.HTTP_200_OK)

