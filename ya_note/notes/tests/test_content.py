from django.test import TestCase

from notes.forms import NoteForm
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
        notes = response.context['object_list']
        self.assertIn(self.note, notes)
        note = notes.get(id=self.note.id)
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

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
