import pytest
from http import HTTPStatus


pytestmark = pytest.mark.django_db

# Константы для статусов
OK = HTTPStatus.OK
FOUND = HTTPStatus.FOUND
NOT_FOUND = HTTPStatus.NOT_FOUND
METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED


def test_home_page_availability(client, home_url):
    """Главная страница доступна анонимному пользователю."""
    response = client.get(home_url)
    assert response.status_code == OK


def test_news_detail_availability(client, detail_url):
    """Страница отдельной новости доступна анонимному пользователю."""
    response = client.get(detail_url)
    assert response.status_code == OK


def test_login_page_availability(client, login_url):
    """Страница входа доступна анонимному пользователю."""
    response = client.get(login_url)
    assert response.status_code == OK


def test_logout_page_behavior(client, logout_url):
    """Страница выхода обрабатывает анонимного пользователя."""
    response = client.get(logout_url)
    assert response.status_code != NOT_FOUND


def test_signup_page_availability(client, signup_url):
    """Страница регистрации доступна анонимному пользователю."""
    response = client.get(signup_url)
    assert response.status_code == OK


def test_edit_page_availability_for_author(author_client, edit_url):
    """Страница редактирования комментария доступна автору комментария."""
    response = author_client.get(edit_url)
    assert response.status_code == OK


def test_delete_page_availability_for_author(author_client, delete_url):
    """Страница удаления комментария доступна автору комментария."""
    response = author_client.get(delete_url)
    assert response.status_code == OK


def test_edit_page_redirects_anonymous_to_login(
        client, edit_url,
        login_url_with_edit_redirect
):
    """
    Анонимный пользователь перенаправляется
    на страницу авторизации при редактировании.
    """
    response = client.get(edit_url)
    assert response.status_code == FOUND
    assert response.url == login_url_with_edit_redirect


def test_delete_page_redirects_anonymous_to_login(
        client, delete_url,
        login_url_with_delete_redirect
):
    """
    Анонимный пользователь перенаправляется
    на страницу авторизации при удалении.
    """
    response = client.get(delete_url)
    assert response.status_code == FOUND
    assert response.url == login_url_with_delete_redirect


def test_edit_page_not_available_for_other_user(admin_client, edit_url):
    """
    Авторизованный пользователь не может
    редактировать чужие комментарии (404).
    """
    response = admin_client.get(edit_url)
    assert response.status_code == NOT_FOUND


def test_delete_page_not_available_for_other_user(admin_client, delete_url):
    """
    Авторизованный пользователь не может
    удалять чужие комментарии (404).
    """
    response = admin_client.get(delete_url)
    assert response.status_code == NOT_FOUND
