from django.test import TestCase, Client
from django.urls import resolve, reverse
from .views import beranda, kampus, event, info, detail, login_view, logout_view, register
import tempfile
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import authenticate
from sukanews.forms import CustomUserCreationForm, CustomAuthenticationForm

class URLTests(TestCase):
    def check_url(self, url_name, view_func, args=None):
        """Helper function untuk test URL + print hasil"""
        try:
            url = reverse(url_name, args=args) if args else reverse(url_name)
            resolved = resolve(url)
            assert resolved.func == view_func, f'❌ URL "{url_name}" gagal: tidak mengarah ke {view_func.__name__}'
            print(f'✅ URL "{url_name}" berhasil mengarah ke view {view_func.__name__}')
        except Exception as e:
            print(str(e))
            raise  # supaya tetap fail di unit test Django

    def test_url_beranda(self):
        self.check_url('beranda', beranda)

    def test_url_kampus(self):
        self.check_url('kampus', kampus)

    def test_url_event(self):
        self.check_url('event', event)

    def test_url_info(self):
        self.check_url('info', info)

    def test_url_read_article(self):
        self.check_url('read-article', detail)

    def test_url_login(self):
        self.check_url('login', login_view)

    def test_url_logout(self):
        self.check_url('logout', logout_view)

    def test_url_register(self):
        self.check_url('register', register)

# view testing
class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_beranda_view(self):
        response = self.client.get(reverse('beranda'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'beranda.html')
        self.assertIn('nama', response.context)
    
    def test_kampus_view(self):
        response = self.client.get(reverse('kampus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kampus.html')
        self.assertIn('nama', response.context)

    def test_event_view(self):
        response = self.client.get(reverse('event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event.html')

    def test_info_view(self):
        response = self.client.get(reverse('info'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'info.html')

    def test_acara_view(self):
        response = self.client.get(reverse('acara'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'acara.html')

    def test_detail_view(self):
        response = self.client.get(reverse('detail'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html')

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post_valid(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        }, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('beranda'))

    def test_login_view_post_invalid(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpass',
        }, follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertContains(response, "Invalid email or password", status_code=200)

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

    def test_logout_view(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(response.context['user'].is_authenticated)

    def test_upload_image_success(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp_file:
            tmp_file.write(b"fake image data")
            tmp_file.seek(0)
            image = SimpleUploadedFile("test.jpg", tmp_file.read(), content_type="image/jpeg")
            response = self.client.post(reverse('upload_image'), {'image': image})
            self.assertEqual(response.status_code, 200)
            self.assertIn('url', response.json())

    def test_upload_image_invalid(self):
        response = self.client.post(reverse('upload_image'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

# test form

class CustomUserCreationFormTests(TestCase):

    def test_valid_form(self):
        form_data = {
            'username': 'validuser',
            'email': 'user@example.com',
            'password1': 'strongPassword123',
            'password2': 'strongPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_username_too_short(self):
        form_data = {
            'username': 'ab',
            'email': 'user@example.com',
            'password1': 'strongPassword123',
            'password2': 'strongPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Username must have at least 3 characters', form.errors['username'])

    def test_username_too_long(self):
        form_data = {
            'username': 'a' * 31,
            'email': 'user@example.com',
            'password1': 'strongPassword123',
            'password2': 'strongPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Username must not exceed 30 characters', form.errors['username'])

    def test_username_with_spaces(self):
        form_data = {
            'username': ' user name ',
            'email': 'user@example.com',
            'password1': 'strongPassword123',
            'password2': 'strongPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'username')

    def test_duplicate_username(self):
        User.objects.create_user(username='dupeuser', password='test1234')
        form_data = {
            'username': 'dupeuser',
            'email': 'newuser@example.com',
            'password1': 'strongPassword123',
            'password2': 'strongPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('This username is already taken', form.errors['username'])

    def test_duplicate_email(self):
        User.objects.create_user(username='anotheruser', email='user@example.com', password='test1234')
        form_data = {
            'username': 'newuser',
            'email': 'user@example.com',
            'password1': 'strongPassword123',
            'password2': 'strongPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('This email is already registered', form.errors['email'])

    def test_optional_email(self):
        form_data = {
            'username': 'usernoemail',
            'email': '',
            'password1': 'strongPassword123',
            'password2': 'strongPassword123',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form_data = {
            'username': 'user1',
            'email': 'user1@example.com',
            'password1': 'Password123',
            'password2': 'DifferentPassword',
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class CustomAuthenticationFormTests(TestCase):

    def setUp(self):
        self.username = 'testuser'
        self.password = 'securepass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_authentication_valid_credentials(self):
        form_data = {
            'username': self.username,
            'password': self.password,
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = authenticate(username=self.username, password=self.password)
        self.assertIsNotNone(user)

    def test_authentication_invalid_credentials(self):
        form_data = {
            'username': self.username,
            'password': 'wrongpassword',
        }
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())