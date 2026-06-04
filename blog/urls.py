from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('categorise',CategoryViewSet)
router.register('posts',PostViewSet)
router.register('commentes',CommentViewSet)


urlpatterns=[
    path('register/',RegisterViwe.as_view()),
    path('logout/',LogoutView.as_view(),name='logout'),
]

urlpatterns += router.urls