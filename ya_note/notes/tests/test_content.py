from django.test import TestCase

from notes.forms import NoteForm
from notes.models import Note
from .fixtures import (
    TestDataMixin,
    NOTES_LIST_URL,
    ADD_NOTE_URL,
    NOTE_EDIT_URL,
)


class TestContent(TestDataMixin, TestCase):

    def test_author_sees_own_notes_in_list(self):
        """Автор видит свои заметки в списке и все поля корректны."""
        response = self.author_client.get(NOTES_LIST_URL)
        author_notes = response.context['object_list']
        self.assertIn(self.note, author_notes)
        # Проверяем ВСЕ поля заметки
        note_from_list = author_notes.get(id=self.note.id)
        self.assertEqual(note_from_list.title, self.note.title)
        self.assertEqual(note_from_list.text, self.note.text)
        self.assertEqual(note_from_list.slug, self.note.slug)
        self.assertEqual(note_from_list.author, self.note.author)

    def test_author_does_not_see_others_notes(self):
        """Автор не видит чужие заметки в списке."""
        # Создаем заметку от другого пользователя
        other_note = Note.objects.create(
            title='Заголовок другого пользователя',
            text='Текст другой заметки',
            slug='other-slug',
            author=self.reader
        )
        response = self.author_client.get(NOTES_LIST_URL)
        author_notes = response.context['object_list']
        self.assertNotIn(other_note, author_notes)

    def test_reader_sees_only_own_notes(self):
        """Читатель видит только свои заметки, не видит заметки автора."""
        # Создаем заметку для читателя
        reader_note = Note.objects.create(
            title='Заметка читателя',
            text='Текст заметки читателя',
            slug='reader-slug',
            author=self.reader
        )
        response = self.reader_client.get(NOTES_LIST_URL)
        reader_notes = response.context['object_list']
        # Читатель должен видеть только свою заметку
        self.assertIn(reader_note, reader_notes)
        self.assertNotIn(self.note, reader_notes)
        self.assertEqual(len(reader_notes), 1)

    def test_pages_contain_forms(self):
        """На страницы создания и редактирования передаются формы."""
        urls_with_forms = [
            ADD_NOTE_URL,
            NOTE_EDIT_URL,
        ]
        for url in urls_with_forms:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
