from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestDataMixin:
    """Фикстуры для тестов заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='test-slug',
            author=cls.author
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def setUp(self):
        self.author_client = self.client_class()
        self.author_client.force_login(self.author)
        self.reader_client = self.client_class()
        self.reader_client.force_login(self.reader)


# URL константы
HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
NOTES_LIST_URL = reverse('notes:list')
ADD_NOTE_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')

# URL с параметрами
NOTE_SLUG = 'test-slug'
NOTE_DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))
NOTE_EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
NOTE_DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))

# URL для перенаправлений
REDIRECT_URLS = {
    NOTES_LIST_URL: f'{LOGIN_URL}?next={NOTES_LIST_URL}',
    SUCCESS_URL: f'{LOGIN_URL}?next={SUCCESS_URL}',
    ADD_NOTE_URL: f'{LOGIN_URL}?next={ADD_NOTE_URL}',
    NOTE_DETAIL_URL: f'{LOGIN_URL}?next={NOTE_DETAIL_URL}',
    NOTE_EDIT_URL: f'{LOGIN_URL}?next={NOTE_EDIT_URL}',
    NOTE_DELETE_URL: f'{LOGIN_URL}?next={NOTE_DELETE_URL}',
}


# Функции для получения URL (если нужны для других slug)
def get_note_detail_url(slug):
    return reverse('notes:detail', args=(slug,))


def get_note_edit_url(slug):
    return reverse('notes:edit', args=(slug,))


def get_note_delete_url(slug):
    return reverse('notes:delete', args=(slug,))
