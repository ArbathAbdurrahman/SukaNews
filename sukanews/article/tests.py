# article/tests.py

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

# Impor dari aplikasi Anda
from .models import Article, Category, Hashtag, Comment, Reply
from .forms import ArticleForm, CommentForm, ReplyForm
from .views import article, detail, create_article, update_article, delete_article, reply_comment

# Diasumsikan ada model Profile untuk redirect di delete_article
from profil.models import Profile


# === KELAS DASAR UNTUK SETUP UMUM ===
class BaseArticleTestCase(TestCase):
    """
    Kelas dasar untuk setup objek yang digunakan berulang kali di berbagai tes.
    Ini mengurangi duplikasi kode secara signifikan.
    """
    @classmethod
    def setUpTestData(cls):
        # Buat user: satu author, satu lagi untuk tes perizinan
        cls.author_user = User.objects.create_user(username='author', password='password123', first_name='Author', last_name='User')
        cls.other_user = User.objects.create_user(username='otheruser', password='password123')
        # Asumsi sinyal membuat Profile, jika tidak, buat manual: Profile.objects.create(user=cls.author_user)

        # Buat kategori dan hashtag
        cls.category1 = Category.objects.create(name='Technology')
        cls.category2 = Category.objects.create(name='Health')
        cls.hashtag1 = Hashtag.objects.create(name='django')
        cls.hashtag2 = Hashtag.objects.create(name='testing')

        # Buat dummy image
        cls.image = SimpleUploadedFile(name='test_img.jpg', content=b'content', content_type='image/jpeg')

        # Buat dua artikel untuk pengujian filtering dan sorting
        cls.article1 = Article.objects.create(
            user=cls.author_user,
            title='The Art of Testing in Django',
            description='A deep dive into unit testing.',
            category=cls.category1,
            content='This content must be at least three hundred words long to pass the form validation. ' * 30,
            image=cls.image
        )
        cls.article1.hashtags.add(cls.hashtag1, cls.hashtag2)

        cls.article2 = Article.objects.create(
            user=cls.author_user,
            title='Healthy Lifestyle with Python',
            description='How Python helps in health.',
            category=cls.category2,
            content='Another long content to pass validation. ' * 30,
            image=cls.image
        )
        cls.article2.hashtags.add(cls.hashtag2)

        # Buat komentar untuk pengujian reply
        cls.comment = Comment.objects.create(
            article=cls.article1,
            user=cls.other_user,
            content='This is a great article!'
        )


# === PENGUJIAN URLS ===
class ArticleURLTests(TestCase):
    def test_url_resolutions(self):
        """Memastikan setiap nama URL me-resolve ke view function yang benar."""
        self.assertEqual(resolve(reverse('article:article')).func, article)
        self.assertEqual(resolve(reverse('article:create')).func, create_article)
        
        # URL dengan argumen
        self.assertEqual(resolve(reverse('article:detail', kwargs={'slug': 'a-slug'})).func, detail)
        self.assertEqual(resolve(reverse('article:update_article', kwargs={'slug': 'a-slug'})).func, update_article)
        self.assertEqual(resolve(reverse('article:delete_article', kwargs={'slug': 'a-slug'})).func, delete_article)
        self.assertEqual(resolve(reverse('article:reply_comment', kwargs={'comment_id': 1})).func, reply_comment)


# === PENGUJIAN MODELS ===
class ArticleModelTests(BaseArticleTestCase):
    def test_model_str_representation(self):
        """Test metode __str__ pada semua model."""
        self.assertEqual(str(self.category1), 'Technology')
        self.assertEqual(str(self.hashtag1), '#django')
        self.assertEqual(str(self.article1), 'The Art of Testing in Django')
        self.assertEqual(str(self.comment), f'Comment by {self.other_user} on {self.article1}')
        
        reply = Reply.objects.create(comment=self.comment, user=self.author_user, content='Thanks!')
        self.assertEqual(str(reply), f'Reply by {self.author_user} on comment {self.comment.id}')

    def test_get_absolute_url(self):
        """Test metode get_absolute_url()."""
        expected_url = reverse('article:detail', kwargs={'slug': self.article1.slug})
        self.assertEqual(self.article1.get_absolute_url(), expected_url)

    def test_get_related_articles(self):
        """Test metode get_related_articles() untuk menemukan artikel terkait."""
        related = self.article1.get_related_articles()
        # article2 terkait karena sama-sama punya hashtag 'testing'
        self.assertIn(self.article2, related)
        # Artikel itu sendiri tidak boleh ada di dalam daftar terkait
        self.assertNotIn(self.article1, related)


# === PENGUJIAN FORMS ===
class ArticleFormTests(BaseArticleTestCase):
    def test_article_form_valid_data(self):
        """Test ArticleForm dengan data yang lengkap dan valid."""
        form_data = {
            'title': 'This is a sufficiently long title for validation',
            'description': 'A valid description.',
            'category': self.category1.id,
            'content': 'This content is also very long, long enough to pass the custom validation rule in the form. ' * 30,
            'hashtags_input': '#new #valid'
        }
        form = ArticleForm(data=form_data, files={'image': self.image})
        self.assertTrue(form.is_valid(), form.errors)

    def test_article_form_title_validation(self):
        """Test validasi panjang title di form."""
        form_data = {'title': 'Too short'}
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('must be at least 20 characters', form.errors['title'][0])

    def test_article_form_hashtags_validation(self):
        """Test validasi jumlah hashtag di form."""
        form_data = {
            'title': 'This is a sufficiently long title for validation',
            'content': 'Valid content ' * 30,
            'hashtags_input': '#a #b #c #d #e #f' # 6 hashtags, melebihi batas
        }
        form = ArticleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('hashtags_input', form.errors)
        self.assertIn('up to 5 hashtags', form.errors['hashtags_input'][0])

    def test_simple_forms_are_valid(self):
        """Test CommentForm dan ReplyForm."""
        comment_form = CommentForm(data={'content': 'A valid comment.'})
        reply_form = ReplyForm(data={'content': 'A valid reply.'})
        self.assertTrue(comment_form.is_valid())
        self.assertTrue(reply_form.is_valid())


# === PENGUJIAN VIEWS ===
class ArticleViewTests(BaseArticleTestCase):
    def setUp(self):
        # Tambahkan client untuk setiap instance test
        self.client = Client()

    def test_article_list_view_with_filters_and_sorting(self):
        """Test halaman daftar artikel dengan berbagai filter dan urutan."""
        url = reverse('article:article')
        
        # 1. Tanpa filter, harus menampilkan semua artikel
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.article1.title)
        self.assertContains(response, self.article2.title)

        # 2. Filter berdasarkan query pencarian (q)
        response = self.client.get(url, {'q': 'Testing in Django'})
        self.assertContains(response, self.article1.title)
        self.assertNotContains(response, self.article2.title)

        # 3. Filter berdasarkan kategori
        response = self.client.get(url, {'category': self.category2.name})
        self.assertNotContains(response, self.article1.title)
        self.assertContains(response, self.article2.title)

        # 4. Sorting (oldest)
        response = self.client.get(url, {'sort_by': 'oldest'})
        # article1 dibuat lebih dulu, jadi harusnya muncul pertama
        # Ini bisa rapuh, tapi untuk demo, kita asumsikan urutannya
        articles_in_context = list(response.context['articles'])
        self.assertEqual(articles_in_context[0].pk, self.article1.pk)

    def test_detail_view_and_commenting(self):
        """Test halaman detail, penambahan view, dan fungsionalitas komentar."""
        url = self.article1.get_absolute_url()
        initial_views = self.article1.views

        # 1. Kunjungan pertama akan menambah view count
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'article_detail.html')
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.views, initial_views + 1)
        
        # 2. Kunjungan kedua (dalam session yang sama) tidak menambah view count
        self.client.get(url)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.views, initial_views + 1)
        
        # 3. Post komentar (harus login)
        self.client.login(username='author', password='password123')
        response = self.client.post(url, data={'content': 'My own new comment!'})
        self.assertRedirects(response, url)
        self.assertTrue(Comment.objects.filter(content='My own new comment!').exists())

    def test_create_article_view(self):
        """Test fungsionalitas pembuatan artikel baru."""
        url = reverse('article:create')
        
        # Redirect jika belum login
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Akses dan POST setelah login
        self.client.login(username='author', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        form_data = {
            'title': 'A Brand New Article Title From Test',
            'description': 'A new valid description.',
            'category': self.category1.id,
            'content': 'This is the long content for the new article created during testing. ' * 30,
            'hashtags_input': '#newarticle #testing'
        }
        response = self.client.post(url, data=form_data, files={'image': self.image})
        self.assertTrue(Article.objects.filter(title__icontains='Brand New Article').exists())
        new_article = Article.objects.get(title__icontains='Brand New Article')
        self.assertRedirects(response, new_article.get_absolute_url())
        self.assertEqual(new_article.hashtags.count(), 2)

    def test_update_and_delete_permissions(self):
        """Test izin untuk update dan delete artikel."""
        update_url = reverse('article:update_article', kwargs={'slug': self.article1.slug})
        delete_url = reverse('article:delete_article', kwargs={'slug': self.article1.slug})

        # 1. User lain (bukan author) tidak bisa mengakses
        self.client.login(username='otheruser', password='password123')
        # Coba update: harus redirect
        response_update = self.client.get(update_url)
        self.assertRedirects(response_update, self.article1.get_absolute_url())
        # Coba delete: harusnya tidak menghapus
        self.client.post(delete_url)
        self.assertTrue(Article.objects.filter(pk=self.article1.pk).exists())
        
        # 2. Author bisa menghapus
        self.client.login(username='author', password='password123')
        response_delete = self.client.post(delete_url)
        profile_url = reverse('profil:profile', kwargs={'username': self.author_user.username})
        self.assertRedirects(response_delete, profile_url)
        self.assertFalse(Article.objects.filter(pk=self.article1.pk).exists())

    def test_reply_comment_view(self):
        """Test fungsionalitas membalas komentar."""
        url = reverse('article:reply_comment', kwargs={'comment_id': self.comment.id})

        # Redirect jika belum login
        response = self.client.post(url, data={'content': 'A reply attempt.'})
        self.assertEqual(response.status_code, 302)

        # Berhasil membalas setelah login
        self.client.login(username='author', password='password123')
        response = self.client.post(url, data={'content': 'This is a valid reply.'})
        self.assertRedirects(response, self.article1.get_absolute_url())
        self.assertTrue(Reply.objects.filter(content='This is a valid reply.', comment=self.comment).exists())