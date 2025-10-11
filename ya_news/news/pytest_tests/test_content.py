import pytest
from django.http import HttpResponseRedirect

from news.models import Comment
from news.forms import BAD_WORDS


pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Тестовый комментарий'}
BAD_FORM_DATA = {'text': f'Текст содержащий {BAD_WORDS[0]}'}
EDIT_FORM_DATA = {'text': 'Обновлённый комментарий'}


def test_anonymous_user_cannot_post_comment(
    client, news, detail_url, login_url_with_redirect
):
    """Анонимный пользователь не может отправить комментарий."""
    comments_before = Comment.objects.count()
    response = client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == comments_before
    assert response.status_code == HttpResponseRedirect.status_code
    login_url, redirect_url = login_url_with_redirect(detail_url)
    assert response.url == redirect_url


def test_authorized_user_can_post_comment(
    author_client, news, author, detail_url
):
    """Авторизованный пользователь может отправить комментарий."""
    comments_before = Comment.objects.count()
    author_client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == comments_before + 1
    new_comment = Comment.objects.latest('id')
    assert new_comment.news == news
    assert new_comment.author == author
    assert new_comment.text == FORM_DATA['text']


def test_comment_with_bad_words_not_published(author_client, news, detail_url):
    """Комментарий с запрещёнными словами не публикуется."""
    comments_before = Comment.objects.count()
    response = author_client.post(detail_url, data=BAD_FORM_DATA)
    assert Comment.objects.count() == comments_before
    assert 'form' in response.context
    assert response.context['form'].errors


def test_author_can_edit_own_comment(author_client, comment, edit_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    original_news = comment.news
    original_author = comment.author
    original_created = comment.created
    response = author_client.post(edit_url, data=EDIT_FORM_DATA)
    assert response.status_code == HttpResponseRedirect.status_code
    comment.refresh_from_db()
    assert comment.text == EDIT_FORM_DATA['text']
    assert comment.news == original_news
    assert comment.author == original_author
    assert comment.created == original_created


def test_author_can_delete_own_comment(author_client, comment, delete_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_before = Comment.objects.count()
    response = author_client.post(delete_url)
    assert Comment.objects.count() == comments_before - 1
    assert response.status_code == HttpResponseRedirect.status_code
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_cannot_edit_others_comment(admin_client, comment, edit_url):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    original_text = comment.text
    original_news = comment.news
    original_author = comment.author
    original_created = comment.created
    response = admin_client.post(edit_url, data={'text': 'Чужой комментарий'})
    assert response.status_code == 404
    comment.refresh_from_db()
    assert comment.text == original_text
    assert comment.news == original_news
    assert comment.author == original_author
    assert comment.created == original_created


def test_user_cannot_delete_others_comment(admin_client, comment, delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comments_before = Comment.objects.count()
    response = admin_client.post(delete_url)
    assert Comment.objects.count() == comments_before
    assert response.status_code == 404
    comment.refresh_from_db()
    assert Comment.objects.filter(id=comment.id).exists()
