from rest_framework import serializers
from django.contrib.auth.models import User
from .models import StudyGroup

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class StudyGroupSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = StudyGroup
        fields = ['id', 'name', 'description', 'creator', 'members']

    def create(self, validated_data):
        group = StudyGroup.objects.create(**validated_data)
        group.members.add(group.creator)  
        return group