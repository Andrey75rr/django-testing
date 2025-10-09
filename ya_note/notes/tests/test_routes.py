from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )

    def test_home_page_available_to_anonymous_user(self):
        """Главная страница доступна анонимному пользователю."""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_pages_availability(self):
        """
        Аутентифицированному пользователю доступны
        страницы notes/, done/, add/.
        """
        self.client.force_login(self.author)
        urls = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_note_pages_available_only_to_author(self):
        """Страницы заметки доступны только автору."""
        self.client.force_login(self.author)
        author_urls = [
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        ]
        for url in author_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
        self.client.force_login(self.reader)
        for url in author_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 404)

    def test_anonymous_user_redirected_to_login(self):
        """Анонимный пользователь перенаправляется на логин."""
        login_url = reverse('users:login')
        urls = [
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
            reverse('notes:detail', args=(self.note.slug,)),
            reverse('notes:edit', args=(self.note.slug,)),
            reverse('notes:delete', args=(self.note.slug,)),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)

    def test_auth_pages_available_to_all_users(self):
        """Страницы регистрации, входа и выхода доступны всем."""
        urls = [
            reverse('users:login'),
            reverse('users:signup'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
        logout_url = reverse('users:logout')
        response = self.client.get(logout_url)
        self.assertIn(response.status_code, [200, 302, 405])
