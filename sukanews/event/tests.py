# event/tests.py

import datetime
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

# Impor dari aplikasi Anda
from .models import Event, Category
from .forms import EventForm
from .views import event, create_event, detail_event, update_event, delete_event


# === KELAS DASAR UNTUK SETUP UMUM ===
class BaseEventTestCase(TestCase):
    """
    Kelas dasar yang menangani setup objek yang sering digunakan di berbagai tes.
    Ini menghindari duplikasi kode dan membuat tes lebih bersih.
    """
    def setUp(self):
        # Buat client untuk request HTTP
        self.client = Client()

        # Buat dua user: satu sebagai author, satu lagi untuk tes perizinan
        self.author_user = User.objects.create_user(username='author', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')

        # Buat kategori
        self.category = Category.objects.create(name='Technology')

        # Buat dummy image untuk upload
        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/jpeg'
        )

        # Buat event utama yang akan digunakan untuk tes update, delete, dan detail
        self.event = Event.objects.create(
            author=self.author_user,
            title='Test Event Title',
            description='A detailed description for this test event.',
            location='Semarang, Indonesia',
            date_start=datetime.date(2025, 10, 10),
            date_end=datetime.date(2025, 10, 11),
            time_start=datetime.time(9, 0),
            time_end=datetime.time(17, 0),
            guidebook='https://example.com/guidebook',
            category=self.category,
            contact='081234567890',
            image=self.image
        )


# === PENGUJIAN URLS ===
class EventURLTests(TestCase):
    def test_url_resolutions(self):
        """Memastikan setiap nama URL me-resolve ke view function yang benar."""
        self.assertEqual(resolve(reverse('event:event')).func, event)
        self.assertEqual(resolve(reverse('event:create_event')).func, create_event)
        
        # URL yang memerlukan argumen slug
        slug_arg = 'some-test-slug'
        self.assertEqual(resolve(reverse('event:detail_event', kwargs={'slug': slug_arg})).func, detail_event)
        self.assertEqual(resolve(reverse('event:update_event', kwargs={'slug': slug_arg})).func, update_event)
        self.assertEqual(resolve(reverse('event:delete_event', kwargs={'slug': slug_arg})).func, delete_event)


# === PENGUJIAN MODELS ===
class EventModelTests(BaseEventTestCase):
    def test_event_creation_and_str(self):
        """Test apakah event dibuat dengan benar dan __str__ mengembalikan title."""
        self.assertEqual(self.event.title, 'Test Event Title')
        self.assertEqual(self.event.author, self.author_user)
        self.assertEqual(str(self.event), 'Test Event Title')

    def test_slug_is_auto_generated_on_save(self):
        """Test bahwa slug dibuat secara otomatis saat menyimpan event baru."""
        self.assertIsNotNone(self.event.slug)
        self.assertTrue(len(self.event.slug) > 0)
        self.assertIn('test-event-title', self.event.slug)

    def test_get_absolute_url(self):
        """Test metode get_absolute_url() mengarah ke URL detail yang benar."""
        expected_url = reverse('event:detail_event', kwargs={'slug': self.event.slug})
        self.assertEqual(self.event.get_absolute_url(), expected_url)


# === PENGUJIAN FORMS ===
class EventFormTests(BaseEventTestCase):
    def test_event_form_is_valid(self):
        """Test EventForm dengan data yang valid."""
        form_data = {
            'title': 'New Valid Event',
            'description': 'Valid description.',
            'category': self.category.id,
            'location': 'Jakarta',
            'date_start': '2025-11-20',
            'date_end': '2025-11-21',
            'time_start': '08:00',
            'time_end': '16:00',
            'guidebook': 'https://example.com/new',
            'contact': '089876543210'
        }
        form = EventForm(data=form_data, files={'image': self.image})
        self.assertTrue(form.is_valid(), form.errors)

    def test_event_form_is_invalid_if_required_field_is_missing(self):
        """Test EventForm tidak valid jika field yang wajib diisi kosong."""
        form_data = {'description': 'Only description is filled.'} # Title kosong
        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('category', form.errors)


# === PENGUJIAN VIEWS ===
class EventViewTests(BaseEventTestCase):
    def test_event_list_view(self):
        """Test halaman daftar event (GET)."""
        response = self.client.get(reverse('event:event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event.html')
        self.assertContains(response, self.event.title)

    def test_event_detail_view_and_views_increment(self):
        """Test halaman detail event (GET) dan memastikan counter 'views' bertambah."""
        initial_views = self.event.views
        url = self.event.get_absolute_url()
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'detail_event.html')
        self.assertContains(response, self.event.title)

        # Cek apakah jumlah views bertambah satu
        self.event.refresh_from_db()
        self.assertEqual(self.event.views, initial_views + 1)

    def test_create_event_view_permissions_and_post(self):
        """Test view create_event (GET dan POST) dan perizinannya."""
        url = reverse('event:create_event')

        # 1. User belum login akan di-redirect
        response = self.client.get(url)
        login_url = reverse('login') # Asumsi nama URL login Anda adalah 'login'
        self.assertRedirects(response, f'{login_url}?next={url}')

        # 2. User sudah login (author) bisa mengakses halaman form
        self.client.login(username='author', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], EventForm)
        
        # 3. POST data valid akan membuat event baru dan redirect
        form_data = {
            'title': 'Event From Post', 'description': 'desc', 'category': self.category.id,
            'location': 'Solo', 'date_start': '2025-12-01', 'date_end': '2025-12-01',
            'time_start': '10:00', 'time_end': '12:00', 'guidebook': 'https://example.com/post',
            'contact': '12345'
        }
        response = self.client.post(url, data=form_data, files={'image': self.image})
        
        # Cek event baru ada di database
        self.assertTrue(Event.objects.filter(title='Event From Post').exists())
        new_event = Event.objects.get(title='Event From Post')
        self.assertRedirects(response, new_event.get_absolute_url())

    def test_update_event_view_permissions(self):
        """Test hanya author yang bisa mengakses halaman update event."""
        url = reverse('event:update_event', kwargs={'slug': self.event.slug})

        # 1. User lain (bukan author) mencoba akses, akan di-redirect
        self.client.login(username='otheruser', password='password123')
        response = self.client.get(url)
        self.assertRedirects(response, self.event.get_absolute_url())

        # 2. Author bisa mengakses halaman update (GET)
        self.client.login(username='author', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # 3. Author melakukan update (POST)
        updated_data = {
            'title': 'Updated Event Title', 'description': self.event.description,
            'category': self.category.id, 'location': self.event.location, 
            'date_start': self.event.date_start, 'date_end': self.event.date_end,
            'time_start': self.event.time_start, 'time_end': self.event.time_end,
            'guidebook': self.event.guidebook, 'contact': self.event.contact
        }
        response = self.client.post(url, data=updated_data, files={'image': self.image})
        self.assertRedirects(response, self.event.get_absolute_url())
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Event Title')

    def test_delete_event_view_permissions(self):
        """Test hanya author yang bisa menghapus event."""
        url = reverse('event:delete_event', kwargs={'slug': self.event.slug})
        event_pk = self.event.pk

        # 1. User lain (bukan author) tidak bisa menghapus
        self.client.login(username='otheruser', password='password123')
        self.client.post(url) # Redirect tidak dites karena view langsung redirect
        self.assertTrue(Event.objects.filter(pk=event_pk).exists()) # Event masih ada

        # 2. Author bisa menghapus
        self.client.login(username='author', password='password123')
        response = self.client.post(url)
        # Asumsi redirect ke profil user
        profile_url = reverse('profil:profile', kwargs={'username': self.author_user.username})
        self.assertRedirects(response, profile_url)
        self.assertFalse(Event.objects.filter(pk=event_pk).exists()) # Event sudah terhapus