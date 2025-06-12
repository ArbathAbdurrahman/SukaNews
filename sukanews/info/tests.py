# info/tests.py

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.text import slugify
import datetime

# Import views, models, and forms from your app
from .views import info, create_info, detail_info, update_info, delete_info, reply_comment
from .models import Info, Category, Comment, Reply
from .forms import InfoForm, CommentForm, ReplyForm

# === KELAS DASAR UNTUK SETUP ===
class BaseInfoTest(TestCase):
    """Kelas dasar untuk setup objek yang digunakan berulang kali."""
    def setUp(self):
        self.client = Client()
        self.author_user = User.objects.create_user(username='author', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        
        self.category = Category.objects.create(name='Test Category')
        
        self.info = Info.objects.create(
            author=self.author_user,
            title='Test Info Title',
            description='This is the content of the test info.',
            category=self.category,
            location='Test Location',
            date=datetime.date.today(),
            time_start=datetime.time(9, 0),
            time_end=datetime.time(10, 0),
            contact='081234567890'
            # slug akan dibuat secara otomatis oleh model
        )
        
        self.comment = Comment.objects.create(
            info=self.info,
            user=self.author_user,
            content='A test comment.'
        )

# === TEST URLS ===
class InfoUrlsTests(TestCase):
    def test_url_resolutions(self):
        """Memastikan semua URL me-resolve ke view yang benar."""
        self.assertEqual(resolve(reverse('info:info')).func, info)
        self.assertEqual(resolve(reverse('info:create_info')).func, create_info)
        self.assertEqual(resolve(reverse('info:detail_info', kwargs={'slug': 'test-slug'})).func, detail_info)
        self.assertEqual(resolve(reverse('info:update_info', kwargs={'slug': 'test-slug'})).func, update_info)
        self.assertEqual(resolve(reverse('info:delete_info', kwargs={'slug': 'test-slug'})).func, delete_info)
        self.assertEqual(resolve(reverse('info:reply_comment', kwargs={'comment_id': 1})).func, reply_comment)

# === TEST VIEWS ===
class InfoViewTests(BaseInfoTest):
    def test_info_list_view(self):
        """Test halaman daftar info."""
        response = self.client.get(reverse('info:info'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('infos', response.context)
        self.assertTemplateUsed(response, 'info/info.html') # Asumsi nama template

    def test_create_info_view(self):
        """Test pembuatan info baru, memerlukan login."""
        url = reverse('info:create_info')
        # 1. User belum login akan di-redirect
        response = self.client.get(url)
        self.assertRedirects(response, f'/accounts/login/?next={url}')

        # 2. User yang sudah login bisa mengakses halaman
        self.client.login(username='author', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], InfoForm)

        # 3. POST data valid akan membuat objek baru dan redirect
        form_data = {
            'title': 'New Info Created',
            'description': 'A new description.',
            'category': self.category.id,
            'location': 'New Location',
            'date': '2025-12-31',
            'time_start': '10:00',
            'time_end': '11:00',
            'contact': '089876543210'
        }
        response = self.client.post(url, form_data)
        self.assertEqual(response.status_code, 302) # Redirect setelah berhasil
        self.assertTrue(Info.objects.filter(title='New Info Created').exists())

    def test_detail_info_view_and_commenting(self):
        """Test halaman detail dan fungsionalitas post komentar."""
        url = reverse('info:detail_info', kwargs={'slug': self.info.slug})
        
        # GET request berhasil
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['info'], self.info)
        
        # POST comment (harus login)
        self.client.login(username='otheruser', password='password123')
        response = self.client.post(url, {'content': 'A new valid comment'})
        self.assertRedirects(response, url) # Redirect ke halaman detail lagi
        self.assertTrue(Comment.objects.filter(content='A new valid comment').exists())

    def test_update_info_permissions_and_post(self):
        """Test izin akses dan fungsionalitas update info."""
        url = reverse('info:update_info', kwargs={'slug': self.info.slug})

        # User lain (bukan author) tidak bisa mengakses, di-redirect
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Author bisa mengakses halaman update
        self.client.login(username='author', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST data untuk update
        update_data = {
            'title': 'Updated Title',
            'description': self.info.description, # Kirim field lain yang required
            'category': self.category.id,
            'location': self.info.location,
            'date': self.info.date,
            'time_start': self.info.time_start,
            'time_end': self.info.time_end,
            'contact': self.info.contact,
        }
        response = self.client.post(url, update_data)
        self.assertRedirects(response, self.info.get_absolute_url())
        self.info.refresh_from_db()
        self.assertEqual(self.info.title, 'Updated Title')

    def test_delete_info_permissions(self):
        """Test izin akses untuk menghapus info."""
        url = reverse('info:delete_info', kwargs={'slug': self.info.slug})
        
        # User lain tidak bisa menghapus
        self.client.login(username='otheruser', password='password123')
        self.client.post(url)
        self.assertTrue(Info.objects.filter(pk=self.info.pk).exists())

        # Author bisa menghapus
        self.client.login(username='author', password='password123')
        response = self.client.post(url)
        self.assertRedirects(response, reverse('info:info')) # Asumsi redirect ke halaman list
        self.assertFalse(Info.objects.filter(pk=self.info.pk).exists())
        
# === TEST FORMS ===
class FormTests(BaseInfoTest):
    def test_info_form_valid(self):
        """Test InfoForm dengan data valid."""
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        form_data = {
            'title': 'Test Title',
            'description': 'This is a description.',
            'category': self.category.id,
            'location': 'Jakarta',
            'date': '2025-06-12',
            'time_start': '09:00',
            'time_end': '10:00',
            'contact': '08123456789',
        }
        form = InfoForm(data=form_data, files={'image': image})
        self.assertTrue(form.is_valid(), form.errors)

    def test_info_form_missing_required_field(self):
        """Test InfoForm tanpa field yang wajib diisi."""
        form_data = {'description': 'some description'} # title tidak diisi
        form = InfoForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_comment_form_valid(self):
        """Test CommentForm dengan data valid."""
        form = CommentForm(data={'content': 'Valid comment.'})
        self.assertTrue(form.is_valid())

    def test_comment_form_empty(self):
        """Test CommentForm dengan data kosong."""
        form = CommentForm(data={'content': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

# === TEST MODELS ===
class ModelTests(BaseInfoTest):
    def test_info_model_str(self):
        """Test representasi string dari model Info."""
        self.assertEqual(str(self.info), 'Test Info Title')

    def test_category_model_str(self):
        """Test representasi string dari model Category."""
        self.assertEqual(str(self.category), 'Test Category')

    def test_info_slug_creation(self):
        """Test slug dibuat otomatis dari title."""
        expected_slug = slugify(self.info.title)
        self.assertTrue(self.info.slug.startswith(expected_slug))

    def test_comment_and_reply_model_str(self):
        """Test representasi string dari model Comment dan Reply."""
        reply = Reply.objects.create(comment=self.comment, user=self.author_user, content='A test reply.')
        self.assertEqual(str(self.comment), f'Comment by {self.author_user.username} on {self.info.title}')
        self.assertEqual(str(reply), f'Reply by {self.author_user.username} on comment {self.comment.id}')