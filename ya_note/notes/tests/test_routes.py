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
        test_cases = [
            (HOME_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),
            (NOTES_LIST_URL, self.author_client, HTTPStatus.OK),
            (SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (ADD_NOTE_URL, self.author_client, HTTPStatus.OK),
            (NOTE_DETAIL_URL, self.author_client, HTTPStatus.OK),
            (NOTE_EDIT_URL, self.author_client, HTTPStatus.OK),
            (NOTE_DELETE_URL, self.author_client, HTTPStatus.OK),
            (NOTE_DETAIL_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTE_EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTE_DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
        ]
        for url, client, expected_status in test_cases:
            with self.subTest(url=url, client=client.__class__.__name__):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)
        response = self.client.get(LOGOUT_URL)
        self.assertNotEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirects(self):
        """Контроль всех перенаправлений."""
        test_cases = [
            (url, expected_redirect)
            for url, expected_redirect in REDIRECT_URLS.items()
        ]
        for url, expected_redirect in test_cases:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
