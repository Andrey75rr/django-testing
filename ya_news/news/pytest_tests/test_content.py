import pytest
from django.http import HttpResponseRedirect

from news.models import Comment


pytestmark = pytest.mark.django_db

FORM_DATA = {'text': 'Тестовый комментарий'}


def test_news_count_on_home_page(client, home_url, multiple_news):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    assert len(object_list) <= 10


def test_news_order(client, home_url, multiple_news):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, detail_url, multiple_comments):
    """Комментарии отсортированы: старые в начале, новые в конце."""
    response = client.get(detail_url)
    news = response.context['news']
    comments = news.comment_set.all()
    if comments.exists():
        all_timestamps = [comment.created for comment in comments]
        sorted_timestamps = sorted(all_timestamps)
        assert all_timestamps == sorted_timestamps


def test_comment_form_availability(client, author_client, detail_url):
    """Анониму недоступна форма комментария, авторизованному доступна."""
    response = client.get(detail_url)
    assert 'form' not in response.context
    response = author_client.get(detail_url)
    assert 'form' in response.context


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
