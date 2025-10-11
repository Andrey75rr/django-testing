import pytest
from http import HTTPStatus


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url_name, client_fixture, expected_status',
    [
        ('home_url', 'client', HTTPStatus.OK),
        ('detail_url', 'client', HTTPStatus.OK),
        ('edit_url', 'author_client', HTTPStatus.OK),
        ('delete_url', 'author_client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('logout_url', 'client', HTTPStatus.METHOD_NOT_ALLOWED),
        ('edit_url', 'client', HTTPStatus.FOUND),
        ('delete_url', 'client', HTTPStatus.FOUND),
        ('edit_url', 'admin_client', HTTPStatus.NOT_FOUND),
        ('delete_url', 'admin_client', HTTPStatus.NOT_FOUND),
    ]
)
def test_pages_availability(
    request, url_name, client_fixture, expected_status
):
    """Проверка доступности страниц с разными кодами ответа."""
    url = request.getfixturevalue(url_name)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_name, client_fixture, redirect_url_name',
    [
        ('edit_url', 'client', 'login_url_with_edit_redirect'),
        ('delete_url', 'client', 'login_url_with_delete_redirect'),
    ]
)
def test_redirects_to_login_page(
    request, url_name, client_fixture, redirect_url_name
):
    """Проверка редиректа анонимных пользователей на страницу логина."""
    url = request.getfixturevalue(url_name)
    client = request.getfixturevalue(client_fixture)
    expected_redirect_url = request.getfixturevalue(redirect_url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect_url
