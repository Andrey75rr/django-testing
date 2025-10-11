from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase

from notes.models import Note
from .fixtures import (
    TestDataMixin,
    ADD_NOTE_URL,
    SUCCESS_URL,
    LOGIN_URL,
    get_note_edit_url,
    get_note_delete_url
)

User = get_user_model()


class TestLogic(TestDataMixin, TestCase):

    def test_authenticated_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        notes_before = set(Note.objects.values_list('id', flat=True))
        response = self.author_client.post(ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        notes_after = set(Note.objects.values_list('id', flat=True))
        new_notes = notes_after - notes_before
        self.assertEqual(len(new_notes), 1)
        new_note = Note.objects.get(id=new_notes.pop())
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_before = set(Note.objects.values_list('id', flat=True))
        response = self.client.post(ADD_NOTE_URL, data=self.form_data)
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(notes_after, notes_before)
        expected_url = f'{LOGIN_URL}?next={ADD_NOTE_URL}'
        self.assertRedirects(response, expected_url)

    def test_cannot_create_duplicate_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        notes_before = set(Note.objects.values_list('id', flat=True))
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(ADD_NOTE_URL, data=self.form_data)
        expected_error = (
            f"{self.note.slug} - такой slug уже существует, "
            "придумайте уникальное значение!"
        )
        self.assertFormError(
            response.context['form'],
            'slug',
            expected_error
        )
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(notes_after, notes_before)

    def test_auto_slug_generation(self):
        """Slug формируется автоматически, если не заполнен."""
        notes_before = set(Note.objects.values_list('id', flat=True))
        form_data = self.form_data.copy()
        form_data.pop('slug')
        response = self.author_client.post(ADD_NOTE_URL, data=form_data)
        self.assertRedirects(response, SUCCESS_URL)
        notes_after = set(Note.objects.values_list('id', flat=True))
        new_notes = notes_after - notes_before
        self.assertEqual(len(new_notes), 1)
        new_note = Note.objects.get(id=new_notes.pop())
        self.assertEqual(new_note.title, form_data['title'])
        self.assertEqual(new_note.text, form_data['text'])
        self.assertTrue(new_note.slug)
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_own_note(self):
        """Пользователь может редактировать свои заметки."""
        note_data_before = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author
        }
        url = get_note_edit_url(self.note.slug)
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.form_data['title'])
        self.assertEqual(updated_note.text, self.form_data['text'])
        self.assertEqual(updated_note.slug, self.form_data['slug'])
        self.assertEqual(updated_note.author, note_data_before['author'])

    def test_author_can_delete_own_note(self):
        """Пользователь может удалять свои заметки."""
        notes_before = set(Note.objects.values_list('id', flat=True))
        self.assertIn(self.note.id, notes_before)
        url = get_note_delete_url(self.note.slug)
        response = self.author_client.post(url)
        self.assertRedirects(response, SUCCESS_URL)
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertNotIn(self.note.id, notes_after)
        self.assertEqual(len(notes_after), len(notes_before) - 1)

    def test_user_cannot_edit_others_note(self):
        """Пользователь не может редактировать чужие заметки."""
        note_data_before = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.note.author
        }
        url = get_note_edit_url(self.note.slug)
        response = self.reader_client.post(url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, note_data_before['title'])
        self.assertEqual(unchanged_note.text, note_data_before['text'])
        self.assertEqual(unchanged_note.slug, note_data_before['slug'])
        self.assertEqual(unchanged_note.author, note_data_before['author'])

    def test_user_cannot_delete_others_note(self):
        """Пользователь не может удалять чужие заметки."""
        notes_before = set(Note.objects.values_list('id', flat=True))
        self.assertIn(self.note.id, notes_before)
        url = get_note_delete_url(self.note.slug)
        response = self.reader_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_after = set(Note.objects.values_list('id', flat=True))
        self.assertEqual(notes_after, notes_before)
        unchanged_note = Note.objects.get(id=self.note.id)
        self.assertEqual(unchanged_note.title, self.note.title)
        self.assertEqual(unchanged_note.text, self.note.text)
        self.assertEqual(unchanged_note.slug, self.note.slug)
        self.assertEqual(unchanged_note.author, self.note.author)
