from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('categories',CategoryViewSet)
router.register('posts',PostViewSet)
router.register('comments',CommentViewSet)


urlpatterns=[
    path('register/',RegisterViwe.as_view(),name='register'),
    path('logout/',LogoutView.as_view(),name='logout'),
]

urlpatterns += router.urls