from http import HTTPStatus

import pytest


pytestmark = pytest.mark.django_db

OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND
METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.parametrize(
    'url_name, client_fixture, expected_status, redirect_url_name',
    [
        ('home_url', 'client', OK, None),
        ('detail_url', 'client', OK, None),
        ('login_url', 'client', OK, None),
        ('signup_url', 'client', OK, None),
        ('logout_url', 'client', METHOD_NOT_ALLOWED, None),
        ('edit_url', 'author_client', OK, None),
        ('delete_url', 'author_client', OK, None),
        ('edit_url', 'admin_client', NOT_FOUND, None),
        ('delete_url', 'admin_client', NOT_FOUND, None),
        ('edit_url', 'client', FOUND, 'login_url_with_edit_redirect'),
        ('delete_url', 'client', FOUND, 'login_url_with_delete_redirect'),
    ]
)
def test_pages_status_codes_and_redirects(
    request, url_name, client_fixture, expected_status, redirect_url_name
):
    """Все проверки статусов и конечных урлов редиректов в одном тесте."""
    url = request.getfixturevalue(url_name)
    client = request.getfixturevalue(client_fixture)
    response = client.get(url)
    assert response.status_code == expected_status
    if redirect_url_name is not None:
        expected_redirect = request.getfixturevalue(redirect_url_name)
        assert response.url == expected_redirect
