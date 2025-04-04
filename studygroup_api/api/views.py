import logging
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

# Set up logger for the 'api' app
logger = logging.getLogger('api')

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
            logger.info(f"User {user.username} registered successfully")
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        logger.error(f"Registration failed: {serializer.errors}")
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
            logger.info(f"User {username} logged in successfully")
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        logger.error(f"Login failed for username {username}: Invalid credentials")
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
            logger.info(f"User {id} details retrieved by {request.user.username}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error(f"User {id} not found")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class StudyGroupListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="List all study groups. Results are paginated (10 per page). Use ?page=2 to access the next page.",
        responses={
            200: openapi.Response('Paginated list of study groups', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of groups'),
                    'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='URL to the next page'),
                    'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='URL to the previous page'),
                    'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(ref='#/components/schemas/StudyGroup'))
                }
            ))
        }
    )
    def get(self, request):
        groups = StudyGroup.objects.all()
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(groups, request)
        serializer = StudyGroupSerializer(page, many=True)
        logger.info(f"Listed study groups (page {request.GET.get('page', 1)})")
        return paginator.get_paginated_response(serializer.data)

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
            logger.info(f"Study group {serializer.data['name']} created by {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Study group creation failed: {serializer.errors}")
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
            logger.error(f"Study group {id} not found")
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudyGroupSerializer(group)
        logger.info(f"Study group {id} details retrieved by {request.user.username}")
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
            logger.error(f"Study group {id} not found for update")
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        if group.creator != request.user:
            logger.warning(f"User {request.user.username} attempted to update study group {id} but is not the creator")
            return Response({'error': 'Only the creator can update this group'}, status=status.HTTP_403_FORBIDDEN)
        serializer = StudyGroupSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Study group {id} updated by {request.user.username}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Study group {id} update failed: {serializer.errors}")
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
            logger.error(f"Study group {id} not found for deletion")
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        if group.creator != request.user:
            logger.warning(f"User {request.user.username} attempted to delete study group {id} but is not the creator")
            return Response({'error': 'Only the creator can delete this group'}, status=status.HTTP_403_FORBIDDEN)
        group.delete()
        logger.info(f"Study group {id} deleted by {request.user.username}")
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
            logger.error(f"Study group {id} not found for joining")
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)
        group.members.add(request.user)
        logger.info(f"User {request.user.username} joined study group {id}")
        return Response({'message': 'Joined group successfully'}, status=status.HTTP_200_OK)

class FlashcardListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="List all flashcards for the authenticated user. Results are paginated (10 per page). Use ?page=2 to access the next page.",
        responses={
            200: openapi.Response('Paginated list of flashcards', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='Total number of flashcards'),
                    'next': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='URL to the next page'),
                    'previous': openapi.Schema(type=openapi.TYPE_STRING, nullable=True, description='URL to the previous page'),
                    'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(ref='#/components/schemas/Flashcard'))
                }
            )),
            401: 'Unauthorized - Authentication required'
        }
    )
    def get(self, request):
        flashcards = Flashcard.objects.filter(user=request.user)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(flashcards, request)
        serializer = FlashcardSerializer(page, many=True)
        logger.info(f"Listed flashcards for {request.user.username} (page {request.GET.get('page', 1)})")
        return paginator.get_paginated_response(serializer.data)

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
            logger.info(f"Flashcard created by {request.user.username}: {serializer.data['front']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Flashcard creation failed: {serializer.errors}")
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
            logger.error(f"Flashcard {id} not found or not authorized for {request.user.username}")
            return Response({'error': 'Flashcard not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FlashcardSerializer(flashcard, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Flashcard {id} updated by {request.user.username}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(f"Flashcard {id} update failed: {serializer.errors}")
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
            logger.error(f"Flashcard {id} not found or not authorized for {request.user.username}")
            return Response({'error': 'Flashcard not found or not authorized'}, status=status.HTTP_404_NOT_FOUND)
        flashcard.delete()
        logger.info(f"Flashcard {id} deleted by {request.user.username}")
        return Response(status=status.HTTP_204_NO_CONTENT)