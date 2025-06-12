# profil/tests.py

from datetime import date
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User

# Import dari aplikasi Anda
from . import views
from .models import Profile, user_directory_path
from .forms import ProfileForm

# Import dari aplikasi lain untuk setup (pastikan field yang diisi lengkap)
from article.models import Article
from event.models import Event
from info.models import Info, Category 

# === KELAS DASAR UNTUK SETUP ===
class BaseProfileTest(TestCase):
    """Kelas dasar untuk setup User dan Profile yang digunakan berulang kali."""
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        # Profile dibuat secara otomatis via signal, kita ambil saja
        self.profile = self.user.profile

# === TEST URLS ===
class ProfilURLTests(BaseProfileTest):
    def test_url_resolution(self):
        """Memastikan URL-namen me-resolve ke view function yang benar."""
        # URL untuk melihat profil
        profile_url = reverse('profil:profile', kwargs={'username': self.user.username})
        self.assertEqual(resolve(profile_url).func, views.profile_view)
        
        # URL untuk mengedit profil
        edit_url = reverse('profil:edit_profile', kwargs={'username': self.user.username})
        self.assertEqual(resolve(edit_url).func, views.edit_profile)

    def test_profile_view_access(self):
        """Test akses ke halaman profil (asumsi profil bersifat publik)."""
        url = reverse('profil:profile', kwargs={'username': self.user.username})
        response = self.client.get(url)
        # Halaman profil publik harusnya bisa diakses siapa saja (status 200)
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_view_access_unauthenticated(self):
        """Test akses halaman edit profil harus redirect jika belum login."""
        url = reverse('profil:edit_profile', kwargs={'username': self.user.username})
        response = self.client.get(url)
        # Harus redirect ke halaman login
        login_url = reverse('login') # Ganti 'login' dengan nama URL login Anda
        self.assertRedirects(response, f'{login_url}?next={url}')

# === TEST MODELS ===
class ProfileModelTest(BaseProfileTest):
    def test_profile_str_method(self):
        """Test representasi string dari model Profile."""
        self.assertEqual(str(self.profile), self.user.username)

    def test_profile_get_full_name(self):
        """Test metode get_full_name pada Profile."""
        self.assertEqual(self.profile.get_full_name(), 'Test User')

    def test_user_directory_path_function(self):
        """Test path upload file yang dihasilkan."""
        path = user_directory_path(self.profile, 'avatar.jpg')
        self.assertEqual(path, f'images/user_{self.user.id}/profile_images_avatar.jpg')

    def test_optional_fields_can_be_blank(self):
        """Test bahwa field opsional bisa kosong tanpa error."""
        self.profile.phone = ''
        self.profile.website = ''
        self.profile.description = ''
        self.profile.about = ''
        self.profile.birth_date = None
        try:
            self.profile.full_clean()  # Validasi model
            self.profile.save()
        except Exception as e:
            self.fail(f"Menyimpan profil dengan field opsional kosong gagal: {e}")

# === TEST VIEWS ===
class ProfileViewsTest(BaseProfileTest):
    def setUp(self):
        """Setup tambahan khusus untuk test view."""
        super().setUp()
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        
        # Pastikan semua field required untuk model lain terisi
        category = Category.objects.create(name='Test Category')
        self.article = Article.objects.create(user=self.user, title='Artikel Tes', content='Konten')
        self.event = Event.objects.create(author=self.user, title='Event Tes', description='Deskripsi')
        self.info = Info.objects.create(author=self.user, title='Info Tes', description='Deskripsi', category=category)

    def test_profile_view_displays_correctly(self):
        """Test bahwa halaman profil menampilkan data yang benar."""
        self.client.login(username='testuser', password='password123')
        url = reverse('profil:profile', kwargs={'username': self.user.username})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profil/profil.html') # Asumsi nama template
        self.assertEqual(response.context['profile'], self.profile)
        self.assertContains(response, self.user.username)
        self.assertIn('articles', response.context)

    def test_edit_profile_get_request(self):
        """Test GET request ke halaman edit profil oleh pemiliknya."""
        self.client.login(username='testuser', password='password123')
        url = reverse('profil:edit_profile', kwargs={'username': self.user.username})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profil/edit_profile.html') # Asumsi nama template
        self.assertIsInstance(response.context['form'], ProfileForm)

    def test_edit_profile_post_request_success(self):
        """Test POST request untuk update profil berhasil."""
        self.client.login(username='testuser', password='password123')
        url = reverse('profil:edit_profile', kwargs={'username': self.user.username})
        post_data = {
            'first_name': 'NamaBaru',
            'last_name': 'AkhirBaru',
            'description': 'Deskripsi baru.',
            # Sertakan field lain jika form Anda membutuhkannya
        }
        response = self.client.post(url, post_data)
        
        profile_url = reverse('profil:profile', kwargs={'username': self.user.username})
        self.assertRedirects(response, profile_url)
        
        # Cek data di database
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        
        self.assertEqual(self.user.first_name, 'NamaBaru')
        self.assertEqual(self.profile.description, 'Deskripsi baru.')
        
    def test_edit_profile_permission_denied_for_other_user(self):
        """Test bahwa user lain tidak bisa mengedit profil."""
        self.client.login(username='otheruser', password='password123')
        url = reverse('profil:edit_profile', kwargs={'username': self.user.username})
        response = self.client.get(url)
        
        # User lain harusnya di-redirect atau mendapat 403 Forbidden
        self.assertEqual(response.status_code, 302) # Atau 403

# === TEST FORMS ===
class ProfileFormTests(BaseProfileTest):
    def test_form_initial_data_is_correct(self):
        """Test bahwa form diinisialisasi dengan data dari instance model."""
        form = ProfileForm(instance=self.profile, user=self.user)
        # Gunakan form.initial untuk mengecek data dari instance
        self.assertEqual(form.initial['first_name'], 'Test')
        self.assertEqual(form.initial['last_name'], 'User')
        self.assertEqual(form.initial['description'], self.profile.description)

    def test_form_saves_correctly(self):
        """Test bahwa form menyimpan data ke User dan Profile dengan benar."""
        form_data = {
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'phone': '089876543210',
            'website': 'https://mywebsite.com',
            'description': 'New description',
            'about': 'About me updated',
            'birth_date': '2000-01-15'
        }
        form = ProfileForm(data=form_data, instance=self.profile, user=self.user)
        
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        
        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.first_name, 'UpdatedFirst')
        self.assertEqual(self.profile.phone, '089876543210')
        self.assertEqual(self.profile.birth_date, date(2000, 1, 15))

    def test_form_is_invalid_with_bad_data(self):
        """Test bahwa form tidak valid jika data tidak sesuai format."""
        form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'website': 'bukan-url-valid'
        }
        form = ProfileForm(data=form_data, instance=self.profile, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)