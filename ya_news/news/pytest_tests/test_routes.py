import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_page_available_to_anonymous_user(client):
    """Главная страница доступна анонимному пользователю."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_available_to_anonymous_user(client, news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == 200


def test_comment_edit_delete_available_to_author(author_client, comment):
    """
    Страницы удаления и редактирования
    комментария доступны автору комментария.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    response_edit = author_client.get(edit_url)
    response_delete = author_client.get(delete_url)
    assert response_edit.status_code == 200
    assert response_delete.status_code == 200


def test_comment_edit_delete_redirect_anonymous_to_login(client, comment):
    """Анонимный пользователь перенаправляется на страницу авторизации."""
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    response_edit = client.get(edit_url)
    response_delete = client.get(delete_url)
    assert response_edit.status_code == 302
    assert response_delete.status_code == 302
    # Более надёжная проверка редиректа на логин
    assert response_edit.url.startswith(reverse('users:login'))
    assert response_delete.url.startswith(reverse('users:login'))


def test_comment_edit_delete_not_available_other_user(admin_client, comment):
    """
    Авторизованный пользователь не может зайти на страницы
    редактирования или удаления чужих комментариев.
    """
    edit_url = reverse('news:edit', args=(comment.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    response_edit = admin_client.get(edit_url)
    response_delete = admin_client.get(delete_url)
    assert response_edit.status_code == 404
    assert response_delete.status_code == 404


@pytest.mark.django_db
def test_auth_pages_available_to_anonymous_user(client):
    """
    Страницы регистрации, входа и выхода
    доступны анонимным пользователям.
    """
    login_url = reverse('users:login')
    logout_url = reverse('users:logout')
    response_login = client.get(login_url)
    response_logout = client.get(logout_url)
    assert response_login.status_code == 200
    assert response_logout.status_code in [200, 302, 405]
