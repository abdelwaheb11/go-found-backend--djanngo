from rest_framework import serializers
from .models import Project, Investment, Commentary, Image
from users.serializers import UserProfileSerializer



# Serializer pour Image
class ImageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Image
        fields = ['id', 'image']

# Serializer pour Project
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id',  'title', 'category', 'description', 'goal_amount', 'raised_amount', 'website_link', 'isActive']

# Serializer pour Investment
class InvestmentSerializer(serializers.ModelSerializer):
    investor = UserProfileSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    
    class Meta:
        model = Investment
        fields = ['id', 'investor', 'project', 'amount', 'created_at']

# Serializer pour Commentary
class CommentarySerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Commentary
        fields = ['id', 'user', 'text', 'created_at', 'image']




