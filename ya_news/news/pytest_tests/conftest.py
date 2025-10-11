from datetime import datetime, timedelta
import pytest
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

from news.models import News, Comment
from django.test import Client


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Создает клиента автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def admin_user(django_user_model):
    """Создает администратора (чужого пользователя)."""
    return django_user_model.objects.create(username='Админ')


@pytest.fixture
def admin_client(admin_user):
    """Создает клиента администратора."""
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Тестовая новость',
        text='Текст тестовой новости'
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Тестовый комментарий'
    )


@pytest.fixture
def multiple_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 5)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def multiple_comments(author, news):
    now = timezone.now()
    for index in range(5):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}'
        )
        comment.created = now + timedelta(hours=index)
        comment.save()


@pytest.fixture
def login_url_with_redirect():
    """Фикстура для создания URL логина с редиректом."""
    def _login_url_with_redirect(next_url):
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={next_url}'
        return login_url, redirect_url
    return _login_url_with_redirect


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def login_url_with_edit_redirect(edit_url, login_url):
    return f'{login_url}?next={edit_url}'


@pytest.fixture
def login_url_with_delete_redirect(delete_url, login_url):
    return f'{login_url}?next={delete_url}'
