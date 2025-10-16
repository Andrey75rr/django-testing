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
    REDIRECT_NOTES_LIST_URL,
    REDIRECT_SUCCESS_URL,
    REDIRECT_ADD_NOTE_URL,
    REDIRECT_NOTE_DETAIL_URL,
    REDIRECT_NOTE_EDIT_URL,
    REDIRECT_NOTE_DELETE_URL
)


class TestRoutes(TestDataMixin, TestCase):

    def test_pages_availability(self):
        """Контроль всех кодов возврата."""
        test_cases = [
            (HOME_URL, self.client, HTTPStatus.OK),
            (LOGIN_URL, self.client, HTTPStatus.OK),
            (SIGNUP_URL, self.client, HTTPStatus.OK),
            (LOGOUT_URL, self.client, HTTPStatus.OK),
            (NOTES_LIST_URL, self.author_client, HTTPStatus.OK),
            (SUCCESS_URL, self.author_client, HTTPStatus.OK),
            (ADD_NOTE_URL, self.author_client, HTTPStatus.OK),
            (NOTE_DETAIL_URL, self.author_client, HTTPStatus.OK),
            (NOTE_EDIT_URL, self.author_client, HTTPStatus.OK),
            (NOTE_DELETE_URL, self.author_client, HTTPStatus.OK),
            (NOTE_DETAIL_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTE_EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTE_DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTES_LIST_URL, self.client, HTTPStatus.FOUND),
            (SUCCESS_URL, self.client, HTTPStatus.FOUND),
            (ADD_NOTE_URL, self.client, HTTPStatus.FOUND),
            (NOTE_DETAIL_URL, self.client, HTTPStatus.FOUND),
            (NOTE_EDIT_URL, self.client, HTTPStatus.FOUND),
            (NOTE_DELETE_URL, self.client, HTTPStatus.FOUND),
        ]
        for url, client, expected_status in test_cases:
            with self.subTest(url=url, client=client.__class__.__name__):
                if url == LOGOUT_URL:
                    response = client.post(url)
                else:
                    response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects(self):
        """Контроль всех перенаправлений."""
        redirect_urls = {
            NOTES_LIST_URL: REDIRECT_NOTES_LIST_URL,
            SUCCESS_URL: REDIRECT_SUCCESS_URL,
            ADD_NOTE_URL: REDIRECT_ADD_NOTE_URL,
            NOTE_DETAIL_URL: REDIRECT_NOTE_DETAIL_URL,
            NOTE_EDIT_URL: REDIRECT_NOTE_EDIT_URL,
            NOTE_DELETE_URL: REDIRECT_NOTE_DELETE_URL,
        }
        for url, expected_redirect in redirect_urls.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
