from http import HTTPStatus

from django.test import TestCase

from .fixtures import (
    TestDataMixin,
    HOME_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL,
    NOTES_LIST_URL,
    ADD_NOTE_URL,
    SUCCESS_URL,
    NOTE_DETAIL_URL,
    NOTE_EDIT_URL,
    NOTE_DELETE_URL,
    REDIRECT_URLS
)


class TestRoutes(TestDataMixin, TestCase):

    def test_pages_availability(self):
        """Контроль всех кодов возврата."""
        # Страницы доступные всем (GET запросы)
        public_urls = [
            HOME_URL,
            LOGIN_URL,
            SIGNUP_URL,
        ]
        for url in public_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        # Страница выхода - доступна всем (не проверяем точный код)
        response = self.client.get(LOGOUT_URL)
        self.assertNotEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Страницы доступные аутентифицированным пользователям
        auth_urls = [
            NOTES_LIST_URL,
            SUCCESS_URL,
            ADD_NOTE_URL,
        ]
        for url in auth_urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        # Страницы заметки доступные только автору
        author_only_urls = [
            NOTE_DETAIL_URL,
            NOTE_EDIT_URL,
            NOTE_DELETE_URL,
        ]
        # Для автора - доступ разрешен
        for url in author_only_urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        # Для другого пользователя - 404
        for url in author_only_urls:
            with self.subTest(url=url):
                response = self.reader_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirects(self):
        """Контроль всех перенаправлений."""
        # Перенаправление анонимного пользователя
        for url, expected_redirect in REDIRECT_URLS.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
