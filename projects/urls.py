from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('', views.ProjectView.as_view(), name='project-list'),  
    path('<int:pk>', views.ProjectView.as_view(), name='project-detail'),  
    path('investments', views.InvestmentView.as_view(),name='investment'),
    path('comments', views.CommentaryView.as_view(),name='comment'),
    path('image/<int:pk>', views.ImageView.as_view(),name='image'),
    path('suggestions', views.SuggestionAPIView.as_view(),name='Suggestions'),
]
