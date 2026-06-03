from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category,Post,Comment,Like


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields  = ['slug']


class CommentSerializer(serializers.ModelSerializer):

    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = [
            'id',
            'user',
            'text',
            'create_at',
        ]


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):

    comments = CommentSerializer(many = True, read_only = True)
    likes_count = serializers.IntegerField(read_only = True)

    author = serializers.SlugRelatedField(read_only = True, slug_field = 'username')
    category = serializers.SlugRelatedField(read_only = True, slug_field = 'name')

    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author','slug']

    def get_liked_by_user(self,obj):
        request = self.context.get('request')
        if request and request.user.is_authenticate:
            return obj.likes.filere(user=request.user).exists()
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