from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Post,Category,Like


class CategoryTests(APITestCase):

    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='rasa113',
            email='bamyani113@gmail.com',
            password='rasa@2003',
            is_staff=True,
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_create_category(self):
        url = reverse('category-list')

        response = self.client.post(
            url,
            {"name": "React"}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class RegisterTests(APITestCase):

# create user
    def test_create_user(self):

        url = reverse('register')

        response = self.client.post(

        url,

        {'username':'rasa2003','email':'rasa2003@gmail.com','password':'rasa@2003','password2':'rasa@2003'}

        )

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        
        self.assertEqual(
            get_user_model().objects.count(),
            1
        )

        user = get_user_model().objects.get(
            username='rasa2003'
        )

        self.assertTrue(
            user.check_password('rasa@2003')
        )


#  password not match
    def test_passwords_do_not_match(self):

        url = reverse('register')

        response = self.client.post(
          url,

           {'username':'rasa2003','email':'rasa2003@gmail.com','password':'rasa@2003','password2':'rasa@20'}

        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)


# invalid datat
    def test_invalid_data(self):
         
        url = reverse('register')

        response = self.client.post(
            url,
            
            {'username':'','email':'rasa2003@gmail.com','password':'rasa@2003','password2':'rasa@20'}
            
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)


# Check duplicate user

    def test_duplicate_username(self):

        url = reverse('register')


        User = get_user_model()

        User.objects.create_user(
            username='rasa2003',
            email='bmayani113@gmail.com',
            password='rasa@2003',
            
        )

        response = self.client.post(
          url,
            
            {'username':'rasa2003','email':'bamyani@gmail.com','password':'rasa@2003','password2':'rasa@2003'}

        ) 

        self.assertEqual(response.status_code , status.HTTP_400_BAD_REQUEST)


# password too short  
    def test_password_too_short(self):
        
        url = reverse('register')


        response = self.client.post(
           url,

           {'username':'eli123','email':'bamyani@gmail.com','password':'123','password2':'123'}
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

        self.assertIn('password',response.data)

        self.assertEqual(get_user_model().objects.count(),0)


class LoginTests(APITestCase):

    def setUp(self):

        self.url = reverse('token_obtain_pair')


        User = get_user_model()

        self.user = User.objects.create_user(
            username='rasa2003',
            email='bmayani113@gmail.com',
            password='rasa@2003',
            
        )

    def test_success_login(self):
 
        response = self.client.post(
           self.url,

            {
                'username' :'rasa2003',
                'password' : 'rasa@2003'
            }
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK)

        self.assertIn('access',response.data)
        self.assertIn('refresh',response.data)


    def test_wrong_password(self):

        response = self.client.post(
           self.url,

            {
                'username' :self.user.username,
                'password' : 'rasa@112'
            }
        )

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

    def test_wrong_username(self):

        response = self.client.post(
           self.url,
           
            {
                'username' :'rasa112',
                'password' : self.user.password,
            }
        )

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

class PermissionTests(APITestCase):
    def setUp(self):
            
        User = get_user_model()

        self.user1 = User.objects.create_user(
            username='owner',
            password='rasa@2003'
        )

        self.user2 = User.objects.create_user(
            username='notowner',
            password='rasa@2003'
        )

        self.client.force_authenticate(user=self.user1)

        self.category = Category.objects.create(name='tech')

        self.post = Post.objects.create(
            title = 'test post',
            content = 'test content',
            category = self.category,
            author = self.user1
        )

    def test_owner_can_update_it(self):

        url = reverse('post-detail',kwargs={'slug':self.post.slug})

        response = self.client.patch(
            url,
            {
                'title':'hello test patch',
                
            }
        )

        self.assertEqual(response.status_code,status.HTTP_200_OK)



    def test_non_owner_cannot_update_it(self):


        url = reverse('post-detail',kwargs={'slug':self.post.slug})

        self.client.force_authenticate(user=self.user2)

        response = self.client.patch(
           url,
            {
                'title':'hacked test title',
                
            }
        )

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)


class LogoutTests(APITestCase):
    
    def setUp(self):
        
        User = get_user_model()

        self.logout_url = reverse('logout')

        self.user = User.objects.create_user(
            username='rasa113',
            password='rasa@2003',
        )        

        self.login_url = reverse('token_obtain_pair')

        self.response = self.client.post(
           self.login_url,

            {
                'username' :'rasa113',
                'password' : 'rasa@2003',
            }
        )

        self.assertEqual(self.response.status_code,status.HTTP_200_OK)

        self.refresh_token = self.response.data['refresh']
        
        self.client.force_authenticate(user=self.user)
        

    def test_send_refresh_token_to_logout(self):

        response = self.client.post(
        self.logout_url,
        {
            'refresh': self.refresh_token
        }

        )

        self.assertEqual(response.status_code,status.HTTP_205_RESET_CONTENT)

    def test_invalid_refresh_token_to_logout(self):

        response = self.client.post(
            self.logout_url,
            {
                'refresh':'fake-token'
            }
        )

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)


class LikeToggleTests(APITestCase):

    def setUp(self):

        User = get_user_model()

        
        
        self.user = User.objects.create_user(
            username='rasa113',
            password='rasa2003',
            
        )


        self.category = Category.objects.create(name='tech')

        self.post = Post.objects.create(
            title = 'test like',
            content = 'test content',
            category = self.category,
            author = self.user
        )

        self.client.force_authenticate(user=self.user)

        self.url = reverse('post-like-toggle',kwargs={'slug':self.post.slug})

    def test_like(self):

        response = self.client.post(self.url)

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

        self.assertTrue(response.data['liked'])

        self.assertTrue(Like.objects.filter(post = self.post,user=self.user).exists())
        
        self.assertEqual(Like.objects.count(),1)

    def test_toggle_like(self):
        
        response1 = self.client.post(self.url)

        self.assertEqual(response1.status_code,status.HTTP_201_CREATED)
        self.assertTrue(response1.data['liked'])

        response2 = self.client.post(self.url)

        self.assertEqual(response2.status_code,status.HTTP_200_OK)
        self.assertFalse(response2.data['liked'])

        self.assertFalse(Like.objects.filter(post=self.post,user=self.user).exists())









    




    


