import pytest
from django.urls import reverse
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    form_data = {'text': 'Тестовый комментарий'}
    response = client.post(url, data=form_data)
    comments_after = Comment.objects.count()
    assert comments_after == comments_before
    assert response.status_code == 302
    # Исправьте URL логина на правильный для вашего проекта
    login_url = reverse('users:login')
    assert login_url in response.url


def test_authorized_user_can_post_comment(author_client, news, author):
    """Авторизованный пользователь может отправить комментарий."""
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    form_data = {'text': 'Тестовый комментарий'}
    author_client.post(url, data=form_data)
    comments_after = Comment.objects.count()
    assert comments_after == comments_before + 1
    new_comment = Comment.objects.filter(news=news, author=author).latest('id')
    assert new_comment.text == 'Тестовый комментарий'
    assert new_comment.news == news
    assert new_comment.author == author


def test_comment_with_bad_words_not_published(author_client, news):
    """Комментарий с запрещёнными словами не публикуется."""
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    form_data = {'text': 'Текст содержащий словоредиска'}
    response = author_client.post(url, data=form_data)
    comments_after = Comment.objects.count()
    assert comments_after == comments_before
    if 'form' in response.context:
        form = response.context['form']
        assert form.errors
    else:
        assert response.status_code != 302


def test_author_can_edit_own_comment(author_client, comment):
    """Авторизованный пользователь может редактировать свои комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    original_text = comment.text
    new_text = 'Обновлённый комментарий'
    response = author_client.post(edit_url, data={'text': new_text})
    assert response.status_code == 302
    comment.refresh_from_db()
    assert comment.text == new_text
    assert comment.text != original_text


def test_author_can_delete_own_comment(author_client, comment):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    comments_before = Comment.objects.count()
    comment_id = comment.id
    response = author_client.post(delete_url)
    comments_after = Comment.objects.count()
    assert comments_after == comments_before - 1
    assert response.status_code == 302
    assert not Comment.objects.filter(id=comment_id).exists()


def test_user_cannot_edit_others_comment(admin_client, comment):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    edit_url = reverse('news:edit', args=(comment.id,))
    original_text = comment.text
    response = admin_client.post(edit_url, data={'text': 'Чужой комментарий'})
    assert response.status_code == 404
    comment.refresh_from_db()
    assert comment.text == original_text


def test_user_cannot_delete_others_comment(admin_client, comment):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    comments_before = Comment.objects.count()
    comment_id = comment.id
    response = admin_client.post(delete_url)
    comments_after = Comment.objects.count()
    assert comments_after == comments_before
    assert response.status_code == 404
    assert Comment.objects.filter(id=comment_id).exists()
