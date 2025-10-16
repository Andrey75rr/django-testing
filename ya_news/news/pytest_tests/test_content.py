import pytest
from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count_on_home_page(client, home_url, multiple_news):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(home_url)
    assert len(
        response.context['object_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, home_url, multiple_news):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(home_url)
    all_dates = [news.date for news in response.context['object_list']]
    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, detail_url, multiple_comments):
    """Комментарии отсортированы: старые в начале, новые в конце."""
    response = client.get(detail_url)
    news = response.context['news']
    comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_comment_form_availability(client, author_client, detail_url):
    """Анониму недоступна форма комментария, авторизованному доступна."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_comment_form_available_to_authorized(author_client, detail_url):
    """Авторизованному пользователю доступна форма комментария."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
