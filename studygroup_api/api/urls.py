from django.urls import path
from .views import RegisterView, LoginView, UserDetailView, StudyGroupListCreateView, StudyGroupDetailView, JoinStudyGroupView

urlpatterns = [
    path('users/register/', RegisterView.as_view(), name='register'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/<int:id>/', UserDetailView.as_view(), name='user_detail'),
    path('groups/', StudyGroupListCreateView.as_view(), name='group_list_create'),
    path('groups/<int:id>/', StudyGroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:id>/join/', JoinStudyGroupView.as_view(), name='join_group'),

]