from http import HTTPStatus

import pytest
from django.http import HttpResponseRedirect

from news.forms import BAD_WORDS
from news.models import Comment


pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Текст из формы комментария'}
BAD_FORM_DATA = {'text': f'Текст содержащий {BAD_WORDS[0]}'}


def test_anonymous_user_cannot_post_comment(
    client, news, detail_url, login_url_with_detail_redirect
):
    """Анонимный пользователь не может отправить комментарий."""
    response = client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 0
    assert response.status_code == HttpResponseRedirect.status_code
    assert response.url == login_url_with_detail_redirect


def test_authorized_user_can_post_comment(
    author_client, news, author, detail_url
):
    """Авторизованный пользователь может отправить комментарий."""
    author_client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.news == news
    assert new_comment.author == author
    assert new_comment.text == FORM_DATA['text']


def test_comment_with_bad_words_not_published(author_client, news, detail_url):
    """Комментарий с запрещёнными словами не публикуется."""
    response = author_client.post(detail_url, data=BAD_FORM_DATA)
    assert Comment.objects.count() == 0
    assert 'form' in response.context
    assert response.context['form'].errors


def test_author_can_edit_own_comment(author_client, comment, edit_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    response = author_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HttpResponseRedirect.status_code
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == FORM_DATA['text']
    assert updated_comment.news == comment.news
    assert updated_comment.author == comment.author


def test_author_can_delete_own_comment(author_client, comment, delete_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    response = author_client.post(delete_url)
    assert not Comment.objects.exists()
    assert response.status_code == HttpResponseRedirect.status_code


def test_user_cannot_edit_others_comment(admin_client, comment, edit_url):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    response = admin_client.post(edit_url, data=FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.news == comment.news
    assert unchanged_comment.author == comment.author


def test_user_cannot_delete_others_comment(admin_client, comment, delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    response = admin_client.post(delete_url)
    assert Comment.objects.count() == 1
    assert response.status_code == HTTPStatus.NOT_FOUND
    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == comment.text
    assert unchanged_comment.news == comment.news
    assert unchanged_comment.author == comment.author
