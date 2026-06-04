
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True,blank=True)

    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True , blank = True)
    content = models.TextField()
    image = models.ImageField(upload_to = 'post/',null = True)

    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)


    def save(self,*args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    

class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    text = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:20]

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='likes')
    user = models.ForeignKey(User,on_delete = models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields = ['post','user'],
                name = 'unique_post_like'
            )
        ]
       


    

    
