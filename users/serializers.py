from django.contrib.auth.models import User
from rest_framework import serializers
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

   

class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.CharField(write_only=True)  
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        
        role = validated_data.pop('role')  
       
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
       
        user_profile = UserProfile.objects.create(
            user=user,
            role=role
        )
        return user_profile


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['user', 'role', 'desc', 'image', 'isActive']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        # Mettre à jour l'utilisateur sans toucher au 'username'
        if user_data:
            username = user_data.get('username', None)
            if username:
                del user_data['username']  # Ne pas modifier le 'username'

            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()

        # Mise à jour des autres champs dans le profil
        instance.role = validated_data.get('role', instance.role)
        instance.desc = validated_data.get('desc', instance.desc)
        instance.image = validated_data.get('image', instance.image)
        instance.isActive = validated_data.get('isActive', instance.isActive)

        instance.save()
        return instance


        
    
    
    

