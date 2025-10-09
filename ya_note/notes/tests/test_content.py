from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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

    def test_note_in_object_list(self):
        """Отдельная заметка передаётся на страницу со списком заметок."""
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_list_contains_only_user_notes(self):
        """В список заметок одного пользователя не попадают заметки другого."""
        # Создаем заметку от другого пользователя
        Note.objects.create(
            title='Заголовок другого пользователя',
            text='Текст',
            slug='other-slug',
            author=self.reader
        )
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        user_notes = Note.objects.filter(author=self.author)
        self.assertEqual(list(object_list), list(user_notes))
        other_user_notes = Note.objects.filter(author=self.reader)
        for note in other_user_notes:
            self.assertNotIn(note, object_list)

    def test_pages_contain_forms(self):
        """На страницы создания и редактирования передаются формы."""
        self.client.force_login(self.author)
        urls_with_forms = [
            reverse('notes:add'),
            reverse('notes:edit', args=(self.note.slug,)),
        ]
        for url in urls_with_forms:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
