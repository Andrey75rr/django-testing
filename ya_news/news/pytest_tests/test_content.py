from django.conf import settings
from django.urls import reverse
import pytest

from news.forms import CommentForm


pytestmark = pytest.mark.django_db

HOME_URL = reverse('news:home')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


def test_news_count_on_home_page(client, multiple_news):
    """Количество новостей на главной странице — не более 10."""
    response = client.get(HOME_URL)
    news_count = len(response.context['object_list'])
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_sorted_by_date(client, multiple_news):
    """Новости отсортированы от самой свежей к самой старой."""
    response = client.get(HOME_URL)
    news_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(news_dates, reverse=True)
    assert news_dates == sorted_dates


def test_comments_sorted_chronologically(
    client, news, multiple_comments, detail_url
):
    """Комментарии отсортированы в хронологическом порядке: старые в начале."""
    response = client.get(detail_url)
    news_obj = response.context['news']
    all_comments = news_obj.comment_set.all()
    comment_times = [comment.created for comment in all_comments]
    sorted_times = sorted(comment_times)
    assert comment_times == sorted_times


def test_comment_form_available_to_authorized(author_client, news, detail_url):
    """Форма комментария доступна авторизованному пользователю."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_comment_form_not_available_to_anonymous(client, news, detail_url):
    """Форма комментария недоступна анонимному пользователю."""
    response = client.get(detail_url)
    assert 'form' not in response.context
