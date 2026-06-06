from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category,Post,Comment,Like
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields  = ['slug']


class CommentSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'text',
            'create_at',
            'replies',
        ]
    def get_replies(self,obj):
        return CommentSerializer(obj.replies.all(),many = True).data


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):

    comments = CommentSerializer(many = True, read_only = True)
    likes_count = serializers.IntegerField(read_only = True)
    liked_by_user = serializers.SerializerMethodField()

    author = serializers.SlugRelatedField(read_only = True, slug_field = 'username')
    category = serializers.SlugRelatedField(read_only = True, slug_field = 'name')

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author','slug']

    def get_liked_by_user(self,obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

        


class RegisterSeralizer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True,min_length = 8)
    password2 = serializers.CharField(write_only = True,min_length = 8)

    class Meta:
        model = User
        fields = ['id','username','email','password','password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {'password':'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):

        validated_data.pop('password2')

        user = User.objects.create_user(
            username= validated_data['username'],
            email=validated_data.get('email',),
            password=validated_data['password'],
            
        )

        return user
    
class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def save(self):
        
        try:
            refresh_token = self.validated_data['refresh']

            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError(
                {'refresh':'Token is invalid or expired'}
            )