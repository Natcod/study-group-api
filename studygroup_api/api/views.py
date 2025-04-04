from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import StudyGroup, Flashcard
from .serializers import UserSerializer, RegisterSerializer, StudyGroupSerializer, FlashcardSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Register a new user and return a token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email of the user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user'),
            },
            required=['username', 'email', 'password']
        ),
        responses={
            201: openapi.Response('User registered successfully', UserSerializer),
            400: 'Bad Request - Invalid input data'
        }
    )
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

    @swagger_auto_schema(
        operation_description="Authenticate a user and return a token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user'),
            },
            required=['username', 'password']
        ),
        responses={
            200: openapi.Response('Login successful', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description='Authentication token')
                }
            )),
            401: 'Unauthorized - Invalid credentials'
        }
    )
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

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific user by ID.",
        responses={
            200: openapi.Response('User details retrieved', UserSerializer),
            404: 'Not Found - User does not exist',
            401: 'Unauthorized - Authentication required'
        }
    )
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class StudyGroupListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="List all study groups.",
        responses={
            200: openapi.Response('List of study groups', StudyGroupSerializer(many=True))
        }
    )
    def get(self, request):
        groups = StudyGroup.objects.all()
        serializer = StudyGroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new study group. The authenticated user is set as the creator.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name of the study group'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description of the study group'),
            },
            required=['name', 'description']
        ),
        responses={
            201: openapi.Response('Study group created', StudyGroupSerializer),
            400: 'Bad Request - Invalid input data',
            401: 'Unauthorized - Authentication required'
        }
    )
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

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific study group by ID.",
        responses={
            200: openapi.Response('Study group details', StudyGroupSerializer),
            404: 'Not Found - Study group does not exist'
        }
    )
    def get(self, request, id):
        group = self.get_object(id)
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudyGroupSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a study group. Only the creator can update the group.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Updated name of the study group'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Updated description of the study group'),
            },
            required=['name', 'description']
        ),
        responses={
            200: openapi.Response('Study group updated', StudyGroupSerializer),
            403: 'Forbidden - Only the creator can update this group',
            404: 'Not Found - Study group does not exist',
            400: 'Bad Request - Invalid input data',
            401: 'Unauthorized - Authentication required'
        }
    )
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

    @swagger_auto_schema(
        operation_description="Delete a study group. Only the creator can delete the group.",
        responses={
            204: 'No Content - Study group deleted successfully',
            403: 'Forbidden - Only the creator can delete this group',
            404: 'Not Found - Study group does not exist',
            401: 'Unauthorized - Authentication required'
        }
    )
    def delete(self, request, id):
        group = self.get_object(id)
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        if group.creator != request.user:
            return Response({'error': 'Only the creator can delete this group'}, status=status.HTTP_403_FORBIDDEN)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class JoinStudyGroupView(APIView):
    @swagger_auto_schema(
        operation_description="Join an existing study group. The authenticated user is added to the group's members.",
        responses={
            200: openapi.Response('Joined group successfully', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                }
            )),
            404: 'Not Found - Study group does not exist',
            401: 'Unauthorized - Authentication required'
        }
    )
    def post(self, request, id):
        group = StudyGroup.objects.filter(id=id).first()
        if not group:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        group.members.add(request.user)
        return Response({'message': 'Joined group successfully'}, status=status.HTTP_200_OK)

class FlashcardListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="List all flashcards for the authenticated user.",
        responses={
            200: openapi.Response('List of flashcards', FlashcardSerializer(many=True)),
            401: 'Unauthorized - Authentication required'
        }
    )
    def get(self, request):
        flashcards = Flashcard.objects.filter(user=request.user)
        serializer = FlashcardSerializer(flashcards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Create a new flashcard for the authenticated user.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'front': openapi.Schema(type=openapi.TYPE_STRING, description='Front side of the flashcard'),
                'back': openapi.Schema(type=openapi.TYPE_STRING, description='Back side of the flashcard'),
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='Category of the flashcard (optional)'),
            },
            required=['front', 'back']
        ),
        responses={
            201: openapi.Response('Flashcard created', FlashcardSerializer),
            400: 'Bad Request - Invalid input data',
            401: 'Unauthorized - Authentication required'
        }
    )
    def post(self, request):
        serializer = FlashcardSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FlashcardDetailView(APIView):
    def get_object(self, id, user):
        try:
            return Flashcard.objects.get(id=id, user=user)
        except Flashcard.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_description="Update a flashcard. Only the owner can update the flashcard.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'front': openapi.Schema(type=openapi.TYPE_STRING, description='Updated front side of the flashcard'),
                'back': openapi.Schema(type=openapi.TYPE_STRING, description='Updated back side of the flashcard'),
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='Updated category of the flashcard (optional)'),
            },
            required=['front', 'back']
        ),
        responses={
            200: openapi.Response('Flashcard updated', FlashcardSerializer),
            404: 'Not Found - Flashcard does not exist or not authorized',
            400: 'Bad Request - Invalid input data',
            401: 'Unauthorized - Authentication required'
        }
    )
    def put(self, request, id):
        flashcard = self.get_object(id, request.user)
        if not flashcard:
            return Response({'error': 'Flashcard not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FlashcardSerializer(flashcard, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a flashcard. Only the owner can delete the flashcard.",
        responses={
            204: 'No Content - Flashcard deleted successfully',
            404: 'Not Found - Flashcard does not exist or not authorized',
            401: 'Unauthorized - Authentication required'
        }
    )
    def delete(self, request, id):
        flashcard = self.get_object(id, request.user)
        if not flashcard:
            return Response({'error': 'Flashcard not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
        flashcard.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)