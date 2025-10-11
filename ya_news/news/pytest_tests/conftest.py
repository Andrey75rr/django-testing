from datetime import datetime, timedelta

import pytest
from django.utils import timezone
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author):
    """Создает клиента автора."""
    from django.test import Client
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
    from django.test import Client
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
