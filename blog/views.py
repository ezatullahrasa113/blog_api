from django.shortcuts import render
from django.db.models import Count
from rest_framework.viewsets import ModelViewSet
from .models import Category,Post,Comment,Like
from .serializers import *
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .premissions import *
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from .pagination import postPagination



class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class PostViewSet(ModelViewSet):

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = postPagination

    lookup_field = 'slug'

    permission_classes = [IsAuthenticatedOrReadOnly,IsAuthorOrReadOnly]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['title', 'content']
    ordering_fields = ['create_at']
    ordering = ['-create_at']

    def perform_create(self, serializer):
        return serializer.save(author = self.request.user)
    
    def get_queryset(self):
        return Post.objects.select_related('author','category').annotate(
            likes_count = Count('likes')
        )
    
    def get_serializer_context(self):
        return {'request':self.request}
    
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like_toggle(self, request, slug=None):
            post = self.get_object()
            user = request.user

            like, created = Like.objects.get_or_create(
                post=post,
                user=user
            )

            if not created:
                like.delete()
                return Response({"liked": False,'likes_count':post.likes_count}, status=status.HTTP_200_OK)

            return Response({"liked": True,'likes_count':post.likes_count},status=status.HTTP_201_CREATED)
            

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,IsCommentOwner]

    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        parent_id = self.request.data.get('parent')

        return serializer.save(user = self.request.user, post_id=post_id, parent_id = parent_id)


class RegisterViwe(APIView):
    def post(self,request):
        serializers = RegisterSeralizer(data =request.data)

        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data,status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = LogoutSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'message':'Successfully logged out'},status=status.HTTP_205_RESET_CONTENT)