from http import HTTPStatus
import pytest
from pytest_lazyfixture import lazy_fixture


pytestmark = pytest.mark.django_db

# Константы для статусов
OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND
METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.parametrize(
    'url, client, expected_status',
    [
        (lazy_fixture('home_url'),
         lazy_fixture('client'), OK),
        (lazy_fixture('detail_url'),
         lazy_fixture('client'), OK),
        (lazy_fixture('login_url'),
         lazy_fixture('client'), OK),
        (lazy_fixture('signup_url'),
         lazy_fixture('client'), OK),
        (lazy_fixture('logout_url'),
         lazy_fixture('client'), METHOD_NOT_ALLOWED),
        (lazy_fixture('edit_url'),
         lazy_fixture('author_client'), OK),
        (lazy_fixture('delete_url'),
         lazy_fixture('author_client'), OK),
        (lazy_fixture('edit_url'),
         lazy_fixture('admin_client'), NOT_FOUND),
        (lazy_fixture('delete_url'),
         lazy_fixture('admin_client'), NOT_FOUND),
        (lazy_fixture('edit_url'),
         lazy_fixture('client'), FOUND),
        (lazy_fixture('delete_url'),
         lazy_fixture('client'), FOUND),
    ]
)
def test_pages_status_codes(url, client, expected_status):
    """Все проверки статусов в одном тесте."""
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_redirect',
    [
        (lazy_fixture('edit_url'),
         lazy_fixture('login_url_with_edit_redirect')),
        (lazy_fixture('delete_url'),
         lazy_fixture('login_url_with_delete_redirect')),
    ]
)
def test_redirects_urls(client, url, expected_redirect):
    """Все проверки конечных урлов редиректов в одном тесте."""
    response = client.get(url)
    assert response.url == expected_redirect
