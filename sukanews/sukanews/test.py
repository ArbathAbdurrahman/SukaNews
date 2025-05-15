from django.test import TestCase
from django.urls import resolve, reverse
from .views import beranda, kampus, event, info, detail, login_view, logout_view, register

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
