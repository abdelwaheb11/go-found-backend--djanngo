from django.urls import path
from .views import RegisterView, LoginView, LogoutView , UserDetailView , UpdateUserProfileView , IsAuthenticated,TopCreatorsAPIView , TopInvestorsAPIView,GetUserByUsername

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('update/', UpdateUserProfileView.as_view(), name='user-update'),
    path('isAuthenticated/', IsAuthenticated.as_view(), name='user-isAuthenticated'),
    path('top-creators/', TopCreatorsAPIView.as_view(), name='top_creators_api'),
    path('top-investors/', TopInvestorsAPIView.as_view(), name='top_investors_api'),
    path('userByUsername/<str:username>', GetUserByUsername.as_view(), name='top_investors_api'),
]
