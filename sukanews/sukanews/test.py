# sukanews/tests.py

from django.test import TestCase, Client
from django.urls import resolve, reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

# Impor dari aplikasi Anda (gunakan path relatif)
from .views import beranda, kampus, event, info, detail, login_view, logout_view, register
from .forms import CustomUserCreationForm, CustomAuthenticationForm

# Asumsi ada model Article untuk halaman detail
from article.models import Article 

# === TEST URLS ===
class SukanewsURLTests(TestCase):
    def test_url_resolutions(self):
        """Memastikan semua URL name me-resolve ke view function yang benar."""
        self.assertEqual(resolve(reverse('beranda')).func, beranda)
        self.assertEqual(resolve(reverse('kampus')).func, kampus)
        self.assertEqual(resolve(reverse('event')).func, event)
        self.assertEqual(resolve(reverse('info')).func, info)
        self.assertEqual(resolve(reverse('login')).func, login_view)
        self.assertEqual(resolve(reverse('logout')).func, logout_view)
        self.assertEqual(resolve(reverse('register')).func, register)
        
        # URL yang butuh argumen (contoh: slug)
        # Buat dummy object dulu untuk mendapatkan slug
        article = Article.objects.create(title="Test Article", content="Test content.", slug="test-article")
        url = reverse('read-article', kwargs={'slug': article.slug})
        self.assertEqual(resolve(url).func, detail)

# === TEST VIEWS ===
class SukanewsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.article = Article.objects.create(title="Test Article", content="Test content.", slug="test-article")

    def test_beranda_view(self):
        response = self.client.get(reverse('beranda'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'beranda.html')

    def test_kampus_view(self):
        response = self.client.get(reverse('kampus'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kampus.html')
        # Cek context jika user login
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('kampus'))
        self.assertIn('nama', response.context)

    def test_detail_view(self):
        url = reverse('read-article', kwargs={'slug': self.article.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail.html') # Asumsi nama template
        self.assertContains(response, self.article.title)

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_view_post_success(self):
        """Test login berhasil harus me-redirect ke beranda."""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        })
        # Cek redirect, bukan halaman final
        self.assertRedirects(response, reverse('beranda'))
        
        # Verifikasi session
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_view_post_invalid(self):
        """Test login gagal akan menampilkan pesan error."""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200) # Tidak redirect
        self.assertContains(response, "Invalid email or password") # Asumsi pesan error
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_logout_view(self):
        """Test logout akan menghapus session dan redirect ke login."""
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertFalse('_auth_user_id' in self.client.session)
        
    # Test untuk upload view Anda (jika ada)
    # def test_upload_image_success(self):
    #     self.client.login(username=self.username, password=self.password)
    #     image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
    #     response = self.client.post(reverse('upload_image'), {'image': image})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('url', response.json())

# === TEST FORMS ===
class CustomUserCreationFormTests(TestCase):
    def test_form_valid(self):
        form_data = {'username': 'newuser', 'email': 'new@test.com', 'password1': 'ValidPass123', 'password2': 'ValidPass123'}
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_username_validation(self):
        """Test validasi panjang dan duplikasi username."""
        # Username sudah ada
        User.objects.create_user(username='exists', password='password')
        form = CustomUserCreationForm(data={'username': 'exists', 'password1': 'p', 'password2': 'p'})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        
        # Username terlalu pendek
        form = CustomUserCreationForm(data={'username': 'a', 'password1': 'p', 'password2': 'p'})
        self.assertFalse(form.is_valid())

    def test_password_mismatch(self):
        """Test jika password1 dan password2 tidak cocok."""
        form_data = {'username': 'user1', 'password1': 'Pass1', 'password2': 'Pass2'}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
    def test_email_is_optional_or_unique(self):
        """Test validasi email (opsional dan unik)."""
        # Email kosong (valid jika opsional)
        form_data = {'username': 'noemail', 'email': '', 'password1': 'p', 'password2': 'p'}
        form = CustomUserCreationForm(data=form_data)
        # Sesuaikan baris berikut dengan aturan form Anda
        self.assertTrue(form.is_valid()) 
        
        # Email duplikat (tidak valid)
        User.objects.create_user('user_with_email', email='duplicate@test.com', password='p')
        form_data = {'username': 'newuser', 'email': 'duplicate@test.com', 'password1': 'p', 'password2': 'p'}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

class CustomAuthenticationFormTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'securepass123'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_auth_form_valid(self):
        """Test form valid dengan kredensial yang benar."""
        form_data = {'username': self.username, 'password': self.password}
        form = CustomAuthenticationForm(data=form_data)
        self.assertTrue(form.is_valid())
        # Form valid akan memiliki user yang terotentikasi
        self.assertEqual(form.get_user(), self.user)

    def test_auth_form_invalid_password(self):
        """Test form tidak valid jika password salah."""
        form_data = {'username': self.username, 'password': 'wrongpassword'}
        form = CustomAuthenticationForm(data=form_data)
        self.assertFalse(form.is_valid())
        # Pastikan user tidak bisa didapatkan dari form
        self.assertIsNone(form.get_user())