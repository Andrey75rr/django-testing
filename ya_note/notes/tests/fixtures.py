from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
NOTES_LIST_URL = reverse('notes:list')
ADD_NOTE_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')

NOTE_SLUG = 'note-slug'
NOTE_DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
NOTE_EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
NOTE_DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))

REDIRECT_NOTES_LIST_URL = f'{LOGIN_URL}?next={NOTES_LIST_URL}'
REDIRECT_SUCCESS_URL = f'{LOGIN_URL}?next={SUCCESS_URL}'
REDIRECT_ADD_NOTE_URL = f'{LOGIN_URL}?next={ADD_NOTE_URL}'
REDIRECT_NOTE_DETAIL_URL = f'{LOGIN_URL}?next={NOTE_DETAIL_URL}'
REDIRECT_NOTE_EDIT_URL = f'{LOGIN_URL}?next={NOTE_EDIT_URL}'
REDIRECT_NOTE_DELETE_URL = f'{LOGIN_URL}?next={NOTE_DELETE_URL}'


class TestDataMixin:
    """Фикстуры для тестов заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug=NOTE_SLUG,
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }
        cls.author_client = cls.client_class()
        cls.author_client.force_login(cls.author)
        cls.reader_client = cls.client_class()
        cls.reader_client.force_login(cls.reader)
