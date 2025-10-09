import pytest
from django.urls import reverse
# from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_on_home_page(client, multiple_news):
    """Количество новостей на главной странице — не более 10."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) <= 10


@pytest.mark.django_db
def test_news_sorted_by_date(client, multiple_news):
    """Новости отсортированы от самой свежей к самой старой."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


@pytest.mark.django_db
def test_comments_sorted_chronologically(client, news, multiple_comments):
    """Комментарии отсортированы в хронологическом порядке: старые в начале."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news = response.context['news']
    comments = news.comment_set.all()
    created_times = [comment.created for comment in comments]
    sorted_times = sorted(created_times)
    assert list(created_times) == sorted_times


@pytest.mark.django_db
def test_comment_form_availability(author_client, news):
    """Форма комментария доступна авторизованному пользователю."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context
