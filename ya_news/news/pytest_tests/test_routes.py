from http import HTTPStatus

import pytest


pytestmark = pytest.mark.django_db

# Константы для статусов
OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND
METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.parametrize(
    'url_name, client_fixture, expected_status',
    [
        ('home_url', 'client', OK),
        ('detail_url', 'client', OK),
        ('login_url', 'client', OK),
        ('signup_url', 'client', OK),
        ('logout_url', 'client', METHOD_NOT_ALLOWED),
        ('edit_url', 'author_client', OK),
        ('delete_url', 'author_client', OK),
        ('edit_url', 'admin_client', NOT_FOUND),
        ('delete_url', 'admin_client', NOT_FOUND),
        ('edit_url', 'client', FOUND),
        ('delete_url', 'client', FOUND),
    ]
)
def test_pages_status_codes(
    request, url_name,
    client_fixture,
    expected_status
):
    """Все проверки статусов в одном тесте."""
    url = request.getfixturevalue(url_name)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_name, redirect_url_name',
    [
        ('edit_url', 'login_url_with_edit_redirect'),
        ('delete_url', 'login_url_with_delete_redirect'),
    ]
)
def test_redirects_urls(client, request, url_name, redirect_url_name):
    """Все проверки конечных урлов редиректов в одном тесте."""
    url = request.getfixturevalue(url_name)
    expected_redirect = request.getfixturevalue(redirect_url_name)
    response = client.get(url)
    assert response.url == expected_redirect
