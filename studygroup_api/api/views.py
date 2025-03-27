from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User  
from .serializers import UserSerializer, RegisterSerializer
from .models import StudyGroup
from .serializers import StudyGroupSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        try:
            user = User.objects.get(id=id) 
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
class StudyGroupListCreateView(APIView):
    def get(self, request):
        groups = StudyGroup.objects.all()
        serializer = StudyGroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StudyGroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudyGroupDetailView(APIView):
    def get_object(self, id):
        try:
            return StudyGroup.objects.get(id=id)
        except StudyGroup.DoesNotExist:
            return None

    def get(self, request, id):
        group = self.get_object(id)
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudyGroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        group = self.get_object(id)
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        if group.creator != request.user:
            return Response({'error': 'Only the creator can update this group'}, status=status.HTTP_403_FORBIDDEN)
        serializer = StudyGroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        group = self.get_object(id)
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        if group.creator != request.user:
            return Response({'error': 'Only the creator can delete this group'}, status=status.HTTP_403_FORBIDDEN)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class JoinStudyGroupView(APIView):
    def post(self, request, id):
        group = StudyGroup.objects.filter(id=id).first()
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        group.members.add(request.user)
        return Response({'message': 'Joined group successfully'}, status=status.HTTP_200_OK)