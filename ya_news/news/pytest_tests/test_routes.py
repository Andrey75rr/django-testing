import pytest
from django.urls import reverse
from http import HTTPStatus


pytestmark = pytest.mark.django_db


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status',
    [
        ('home_url', 'client', HTTPStatus.OK),
        ('detail_url', 'client', HTTPStatus.OK),
        ('edit_url', 'author_client', HTTPStatus.OK),
        ('delete_url', 'author_client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('logout_url', 'client', HTTPStatus.METHOD_NOT_ALLOWED),
    ]
)
def test_pages_availability(
    request, url_fixture, client_fixture, expected_status
):
    """Проверка доступности страниц с разными кодами ответа."""
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url_fixture, client_fixture, expected_status, should_redirect',
    [
        ('edit_url', 'client', HTTPStatus.FOUND, True),
        ('delete_url', 'client', HTTPStatus.FOUND, True),
        ('edit_url', 'admin_client', HTTPStatus.NOT_FOUND, False),
        ('delete_url', 'admin_client', HTTPStatus.NOT_FOUND, False),
    ]
)
def test_redirects_and_errors(
    request, url_fixture, client_fixture, expected_status, should_redirect
):
    """Проверка редиректов и ошибок доступа."""
    url = request.getfixturevalue(url_fixture)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status
    if should_redirect:
        expected_redirect_url = reverse('users:login') + f'?next={url}'
        assert response.url == expected_redirect_url
