from http import HTTPStatus

import pytest


pytestmark = pytest.mark.django_db

# Константы для статусов
OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND
METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.parametrize(
    'url, client, expected_status',
    [
        (pytest.lazy_fixture('home_url'),
         pytest.lazy_fixture('anon_client'), OK),
        (pytest.lazy_fixture('detail_url'),
         pytest.lazy_fixture('anon_client'), OK),
        (pytest.lazy_fixture('login_url'),
         pytest.lazy_fixture('anon_client'), OK),
        (pytest.lazy_fixture('signup_url'),
         pytest.lazy_fixture('anon_client'), OK),
        (pytest.lazy_fixture('logout_url'),
         pytest.lazy_fixture('anon_client'), METHOD_NOT_ALLOWED),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('author_client'), OK),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('author_client'), OK),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('admin_client'), NOT_FOUND),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('admin_client'), NOT_FOUND),
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('anon_client'), FOUND),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('anon_client'), FOUND),
    ]
)
def test_pages_status_codes(url, client, expected_status):
    """Все проверки статусов в одном тесте."""
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_redirect',
    [
        (pytest.lazy_fixture('edit_url'),
         pytest.lazy_fixture('login_url_with_edit_redirect')),
        (pytest.lazy_fixture('delete_url'),
         pytest.lazy_fixture('login_url_with_delete_redirect')),
    ]
)
def test_redirects_urls(anon_client, url, expected_redirect):
    """Все проверки конечных урлов редиректов в одном тесте."""
    response = anon_client.get(url)
    assert response.status_code == FOUND
    assert response.url == expected_redirect
