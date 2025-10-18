import pytest
from pytest_lazy_fixtures import lf
from http import HTTPStatus

pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND
METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.parametrize(
    'url, client_name, expected_status',
    [
        (lf('home_url'), 'client', OK),
        (lf('detail_url'), 'client', OK),
        (lf('login_url'), 'client', OK),
        (lf('signup_url'), 'client', OK),
        (lf('logout_url'), 'client', METHOD_NOT_ALLOWED),
        (lf('edit_url'), 'author_client', OK),
        (lf('delete_url'), 'author_client', OK),
        (lf('edit_url'), 'admin_client', NOT_FOUND),
        (lf('delete_url'), 'admin_client', NOT_FOUND),
        (lf('edit_url'), 'client', FOUND),
        (lf('delete_url'), 'client', FOUND),
    ]
)
def test_pages_status_codes(request, url, client_name, expected_status):
    """Все проверки статусов в одном тесте."""
    client = request.getfixturevalue(client_name)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, redirect_url',
    [
        (lf('edit_url'), lf('login_url_with_edit_redirect')),
        (lf('delete_url'), lf('login_url_with_delete_redirect')),
    ]
)
def test_redirects_urls(request, url, redirect_url):
    """Все проверки конечных урлов редиректов в одном тесте."""
    client = request.getfixturevalue('client')
    response = client.get(url)
    assert response.status_code == FOUND
    assert response.url == redirect_url
