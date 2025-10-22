from http import HTTPStatus

import pytest


pytestmark = pytest.mark.django_db

# Константы для статусов
OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND
METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED

ANON_CLIENT = 'client'
AUTHOR_CLIENT = 'author_client'
ADMIN_CLIENT = 'admin_client'
HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
SIGNUP_URL = pytest.lazy_fixture('signup_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
LOGIN_URL_WITH_EDIT_REDIRECT = pytest.lazy_fixture(
    'login_url_with_edit_redirect'
)
LOGIN_URL_WITH_DELETE_REDIRECT = pytest.lazy_fixture(
    'login_url_with_delete_redirect'
)


@pytest.mark.parametrize(
    'url, client_fixture, expected_status',
    [
        (HOME_URL, ANON_CLIENT, OK),
        (DETAIL_URL, ANON_CLIENT, OK),
        (LOGIN_URL, ANON_CLIENT, OK),
        (SIGNUP_URL, ANON_CLIENT, OK),
        (LOGOUT_URL, ANON_CLIENT, METHOD_NOT_ALLOWED),
        (EDIT_URL, AUTHOR_CLIENT, OK),
        (DELETE_URL, AUTHOR_CLIENT, OK),
        (EDIT_URL, ADMIN_CLIENT, NOT_FOUND),
        (DELETE_URL, ADMIN_CLIENT, NOT_FOUND),
        (EDIT_URL, ANON_CLIENT, FOUND),
        (DELETE_URL, ANON_CLIENT, FOUND),
    ]
)
def test_pages_status_codes(url, client_fixture, expected_status, request):
    """Все проверки статусов в одном тесте."""
    response = request.getfixturevalue(client_fixture).get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_redirect',
    [
        (EDIT_URL, LOGIN_URL_WITH_EDIT_REDIRECT),
        (DELETE_URL, LOGIN_URL_WITH_DELETE_REDIRECT),
    ]
)
def test_redirects_urls(client, url, expected_redirect):
    """Все проверки конечных урлов редиректов в одном тесте."""
    response = client.get(url)
    assert response.url == expected_redirect
