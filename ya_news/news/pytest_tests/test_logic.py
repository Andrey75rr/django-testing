import pytest
from django.http import HttpResponseRedirect
from news.models import Comment
from django.urls import reverse


pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Тестовый комментарий'}
BAD_FORM_DATA = {'text': 'Текст содержащий словоредиска'}
EDIT_FORM_DATA = {'text': 'Обновлённый комментарий'}


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


def test_anonymous_user_cannot_post_comment(client, news, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    comments_before = Comment.objects.count()
    response = client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == comments_before
    assert response.status_code == HttpResponseRedirect.status_code
    assert response.url == reverse('users:login') + f'?next={detail_url}'


def test_authorized_user_can_post_comment(
    author_client, news, author, detail_url
):
    """Авторизованный пользователь может отправить комментарий."""
    comments_before = Comment.objects.count()
    author_client.post(detail_url, data=FORM_DATA)
    assert Comment.objects.count() == comments_before + 1
    new_comment = Comment.objects.get(
        news=news, author=author, text=FORM_DATA['text']
    )
    assert new_comment.news == news
    assert new_comment.author == author


def test_comment_with_bad_words_not_published(author_client, news, detail_url):
    """Комментарий с запрещёнными словами не публикуется."""
    comments_before = Comment.objects.count()
    response = author_client.post(detail_url, data=BAD_FORM_DATA)
    assert Comment.objects.count() == comments_before
    assert 'form' in response.context
    assert response.context['form'].errors


def test_author_can_edit_own_comment(author_client, comment, edit_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    original_comment = Comment.objects.get(id=comment.id)
    response = author_client.post(edit_url, data=EDIT_FORM_DATA)
    assert response.status_code == HttpResponseRedirect.status_code
    updated_comment = Comment.objects.get(id=comment.id)
    assert updated_comment.text == EDIT_FORM_DATA['text']
    assert updated_comment.news == original_comment.news
    assert updated_comment.author == original_comment.author


def test_author_can_delete_own_comment(author_client, comment, delete_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    comments_before = Comment.objects.count()
    response = author_client.post(delete_url)
    assert Comment.objects.count() == comments_before - 1
    assert response.status_code == HttpResponseRedirect.status_code
    assert not Comment.objects.filter(id=comment.id).exists()


def test_user_cannot_edit_others_comment(admin_client, comment, edit_url):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    original_comment = Comment.objects.get(id=comment.id)
    response = admin_client.post(edit_url, data={'text': 'Чужой комментарий'})
    assert response.status_code == 404
    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == original_comment.text
    assert unchanged_comment.news == original_comment.news
    assert unchanged_comment.author == original_comment.author


def test_user_cannot_delete_others_comment(admin_client, comment, delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    original_comment = Comment.objects.get(id=comment.id)
    comments_before = Comment.objects.count()
    response = admin_client.post(delete_url)
    assert Comment.objects.count() == comments_before
    assert response.status_code == 404
    unchanged_comment = Comment.objects.get(id=comment.id)
    assert unchanged_comment.text == original_comment.text
    assert unchanged_comment.news == original_comment.news
    assert unchanged_comment.author == original_comment.author
    assert unchanged_comment.created == original_comment.created
