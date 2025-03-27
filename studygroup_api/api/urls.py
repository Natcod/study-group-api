from django.urls import path
from .views import RegisterView, LoginView, UserDetailView

urlpatterns = [
    path('users/register/', RegisterView.as_view(), name='register'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user_detail'),
]